import streamlit
from pathlib import Path
import uuid
import zipfile
from agent import doc_graph
from services import state_service

MAX_FILE_SIZE = 100_000  #Bytes
MAX_ZIP_SIZE = 10 * 1024 * 1024 #10 MB
MAX_FILES_IN_ZIP = 100

RELEVANT_EXTENSIONS = {".py", ".sql"}

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

def _read_file(file) -> str:
    return file.read().decode("utf-8")

def handle_upload(file) -> None:
    if file is None:
        return

    file_name = file.name

    #Comprueba si es un proyecto o un fichero independiente
    if file_name.endswith(".zip"):
        project_path = _extract_zip(file)
        if project_path:
            state_service.set_current_project(str(project_path), file_name)
            state_service.clear_last_documentation()
            streamlit.success(f"Proyecto extraído: {file_name}")
    else:
        code = _read_file(file)

        if len(code) > MAX_FILE_SIZE:
            streamlit.error(f"El archivo es más grande de lo permitido: {MAX_FILE_SIZE}.")
            return

        result = _get_graph().invoke({
            "code": code,
            "filename": file.name,
            "documentation": "",
        })

        state_service.set_last_documentation(result["documentation"])


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
    return any(path.endswith(ext) for ext in RELEVANT_EXTENSIONS)

def _extract_zip(uploaded_file) -> Path | None:
    #Comprobamos el size del zip
    uploaded_file.seek(0, 2)
    size = uploaded_file.tell()
    uploaded_file.seek(0)

    if size > MAX_ZIP_SIZE:
        streamlit.error(f"El Zip es demasiado grande. Máximo permitido: {MAX_ZIP_SIZE} MB")
        return None

    #Creamos un nuevo directorio para el proyecto
    project_id = str(uuid.uuid4())
    extract_dir = UPLOADS_DIR / project_id
    extract_dir.mkdir(parents = True, exist_ok = True)

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

                # Validar path traversal
                if not _is_safe_zip_member(member.filename, extract_dir):
                    streamlit.warning(f"Se ha ignorado una entrada insegura: {member.filename}")
                    continue

                # Validar tamaño por archivo
                if member.file_size > MAX_FILE_SIZE:
                    continue

                # Contar solo archivos relevantes
                if _has_relevant_extension(member.filename):
                    file_count += 1
                    if file_count > MAX_FILES_IN_ZIP:
                        streamlit.warning(f"El ZIP contiene más de {MAX_FILES_IN_ZIP} archivos relevantes. "
                                   "Se ignorarán los restantes.")
                        break

                # Extraer el archivo (seguro)
                zf.extract(member, extract_dir)

    except zipfile.BadZipFile:
        streamlit.error("El archivo no es un ZIP válido.")
        return None

    return extract_dir