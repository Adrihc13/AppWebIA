import uuid
import zipfile
from pathlib import Path

import streamlit

from agent import doc_graph
from services import state_service
from utils import constants as const
from repositories import project_repo, file_repo

IGNORED_FOLDERS = {
    "__pycache__",
    ".git", ".idea", ".vscode", ".pytest_cache", ".mypy_cache",
    ".venv", "venv", "env",
    "node_modules",
    "dist", "build",
    ".tox", ".cache",
}

UPLOADS_DIR = Path("data/uploads")

@streamlit.cache_resource
def _get_graph():
    return doc_graph.build_graph()

# --- Utils ---

def _read_file(file) -> str:
    return file.read().decode("utf-8")

#Comprueba si el fichero existe en el path del proyecto por seguridad
def _is_safe_zip_member(member_name: str, extract_dir: Path) -> bool:
    try:
        base = extract_dir.resolve()
        target = (extract_dir / member_name).resolve()

        return str(target).startswith(str(base))
    except (ValueError, OSError):
        return False

def _is_in_ignored_folder(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(part in IGNORED_FOLDERS for part in parts)

def _has_relevant_extension(path: str) -> bool:
    return any(path.endswith(ext) for ext in const.RELEVANT_EXTENSIONS)

# --- process .zip ---

def _process_zip(uploaded_file) -> str | None:
    #Comprobamos el size del zip
    uploaded_file.seek(0, 2)
    size = uploaded_file.tell()
    uploaded_file.seek(0)

    if size > const.MAX_ZIP_SIZE:
        streamlit.error(f"El Zip es demasiado grande. Máximo permitido: {const.MAX_ZIP_SIZE} MB")
        return None

    #Creamos un nuevo directorio para el proyecto
    project_id = str(uuid.uuid4())
    name = uploaded_file.name
    project_repo.create(project_id, name)

    try:
        with zipfile.ZipFile(uploaded_file) as zf:
            file_count = 0

            for member in zf.infolist():
                # Ignorar directorios
                if member.is_dir():
                    continue

                # Ignorar carpetas excluidas
                if _is_in_ignored_folder(member.filename):
                    continue

                if not _has_relevant_extension(member.filename):
                    continue

                # Validar path traversal
                if not _is_safe_zip_member(member.filename, Path(".")):
                    streamlit.warning(f"Se ha ignorado una entrada insegura: {member.filename}")
                    continue

                # Validar tamaño por archivo
                if member.file_size > const.MAX_FILE_SIZE:
                    continue

                if file_count > const.MAX_FILES_IN_ZIP:
                    streamlit.warning(f"El ZIP contiene más de {const.MAX_FILES_IN_ZIP} archivos relevantes. "
                        "Se ignorarán los restantes.")
                    break

                content = zf.read(member).decode("utf-8", errors="ignore")
                file_repo.create(project_id, member.filename, content)
                file_count += 1

    except zipfile.BadZipFile:
        project_repo.delete(project_id)
        streamlit.error("El archivo no es un ZIP válido.")
        return None

    except Exception as e:
        project_repo.delete(project_id)
        streamlit.error(f"Error al procesar el ZIP: {e}")
        return None

    return project_id


# --- process tree ---

# Ahora se construye el arbol desde la base de datos en vez de recorrer los directorios
def _build_tree_from_files(project_id: str) -> dict | None:
    files = file_repo.get_by_project(project_id)
    if not files:
        return None

    root = {
        "name": "root",
        "type": "folder",
        "children": [],
    }

    for file in files:
        parts = file["relative_path"].replace("\\", "/").split("/")
        current = root

        # Carpetas intermedias entre el archivo final y el root (recorremos toda la lista excepto el ultimo/fichero)
        for part in parts[:-1]:
            existing = next(
                (c for c in current["children"] if c["name"] == part and c["type"] == "folder"),
                None,
            )
            if not existing:
                existing = {
                    "name": part,
                    "type": "folder",
                    "children": [],
                }
                current["children"].append(existing)
            current = existing

        # Archivo final
        current["children"].append({
            "name": parts[-1],
            "type": "file",
            "path": file["relative_path"],
            "selectable": True,
        })

    # Ordenar: carpetas primero, luego archivos, alfabético
    _sort_tree(root)

    return root


def _sort_tree(node: dict) -> None:
    children = node.get("children", [])
    children.sort(key=lambda c: (c["type"] != "folder", c["name"].lower()))
    for child in children:
        if child["type"] == "folder":
            _sort_tree(child)


@streamlit.cache_data(show_spinner=False)
def _get_cached_tree(project_id: str) -> dict | None:
    return _build_tree_from_files(project_id)


def get_project_tree() -> dict | None:
    project = state_service.get_current_project()
    if not project:
        return None
    project_id, _ = project
    return _get_cached_tree(project_id)


# --- Documentar archivos ---

def document_selected_file(relative_path: str) -> None:
    project = state_service.get_current_project()
    if not project:
        streamlit.error("No hay proyecto cargado.")
        return

    project_id, _ = project

    # Leer de BBDD
    content = file_repo.get_content(project_id, relative_path)
    if content is None:
        streamlit.error(f"No se encontró el archivo: {relative_path}")
        return

    # Validar tamaño
    if len(content) > const.MAX_FILE_SIZE:
        streamlit.error(
            f"El archivo es demasiado grande "
            f"({len(content):,} caracteres). Máximo: {const.MAX_FILE_SIZE:,}."
        )
        return

    # Validar vacío
    if not content.strip():
        streamlit.toast(f"`{Path(relative_path).name}` está vacío", icon="⚠️")
        return

    # Guardar el archivo seleccionado en session_state
    state_service.set_selected_file(relative_path, content)

    # Invocar al grafo
    result = _get_graph().invoke({
        "code": content,
        "filename": relative_path,
        "documentation": "",
    })

    doc = result["documentation"]

    # Guardar doc en session_state y en BBDD
    state_service.set_last_documentation(doc)
    file_repo.update_documentation(project_id, relative_path, doc)


def document_uploaded_file(name: str, content: str) -> None:
    if len(content) > const.MAX_FILE_SIZE:
        streamlit.error(
            f"El archivo es demasiado grande "
            f"({len(content):,} caracteres). Máximo: {const.MAX_FILE_SIZE:,}."
        )
        return

    if not content.strip():
        streamlit.toast(f"`{Path(name).name}` está vacío", icon="⚠️")
        return

    # Guardar el archivo subido
    state_service.set_uploaded_file(name, content)

    result = _get_graph().invoke({
        "code": content,
        "filename": name,
        "documentation": "",
    })

    state_service.set_last_documentation(result["documentation"])


# --- Handler principal ---

def handle_upload(uploaded_file) -> None:
    """Procesa el archivo subido: .py → doc, .zip → proyecto."""
    if uploaded_file is None:
        return

    filename = uploaded_file.name

    if filename.endswith(".zip"):
        project_id = _process_zip(uploaded_file)
        if project_id:
            state_service.set_current_project(project_id, filename)
            state_service.clear_documentation()
            streamlit.success(f"Proyecto cargado: {filename}")
    else:
        code = _read_file(uploaded_file)
        document_uploaded_file(filename, code)