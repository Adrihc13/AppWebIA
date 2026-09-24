import streamlit
from pathlib import Path
from services import doc_service, state_service

def _render_header() -> None:
    streamlit.title("📄 Documentador de código")
    streamlit.markdown("Sube un archivo .py o un .zip de tu proyecto de Python y obtén documentación técnica generada por un Agente de IA")
    streamlit.caption("(Evita incluir el .venv del .zip)  \n Para cualquier duda o consulta, una vez generada la documentación puedes preguntar al agente sobre ese fichero, " \
    "mediante un boton que aparecera en la parte superior de la documentación")

def _render_uploader() -> None:
    file = streamlit.file_uploader(
        "Selecciona un archivo .py a analizar",
        type = ["py", "zip"],
        accept_multiple_files = False,
        max_upload_size = 10
    )

    if file is not None:
        col1, col2 = streamlit.columns([1,4])
        with col1:
            if streamlit.button("📝 Documentar", type = "primary", use_container_width = True):
                doc_service.handle_upload(file)
                streamlit.rerun()



def _render_tree_node(node: dict, depth: int = 0) -> None:
    if depth > 0:
        col_left, col_right = streamlit.columns([depth, 20])
        with col_right:
            _render_node_content(node, depth)
    else:
        _render_node_content(node, depth)
        
def _render_node_content(node: dict, depth: int) -> None:
    if node["type"] == "folder":
        streamlit.markdown(f"📁 **{node['name']}**")
        for child in node.get("children", []):
            _render_tree_node(child, depth + 1)
    else:
        if node.get("selectable"):
            if streamlit.button(
                f"📄 {node['name']}",
                key=f"tree_file_{node['path']}",
                ):
                with streamlit.spinner(f"Documentando {node['name']}..."):
                    doc_service.document_selected_file(node["path"])

                streamlit.rerun()
        else:
            streamlit.markdown(f"📄 {node['name']}")

def _render_tree(tree: dict | None) -> None:
    if not tree:
        streamlit.info("No se ha cargado ningún proyecto")
        return

    # CSS para el espacio vertical entre lineas del arbol
    streamlit.markdown(
        """
        <style>
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.15rem !important;
        }
        div[data-testid="stButton"] > button {
            padding: 0.1rem 0.4rem !important;
            min-height: 1.6rem !important;
            line-height: 1.0 !important;
        }
        div[data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.4 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    streamlit.subheader("🌳 Estructura 🌳")
    _render_tree_node(tree)

#Caso de que se suba un proyecto
def _render_file_documentation() -> None:
    selected = state_service.get_selected_file()
    if not selected:
        return

    path, content = selected
    doc = state_service.get_last_documentation()

    # Botón de volver
    col1, col2, _ = streamlit.columns([4, 8, 10])
    with col1:
        if streamlit.button("← Volver al árbol", use_container_width=True):
            state_service.clear_selected_file()
            state_service.clear_last_documentation()
            streamlit.rerun()
    with col2:
        if streamlit.button("💬 Preguntar al Agente", use_container_width=True, type="primary"):
            from services import chat_service
            chat_service.start_chat_with_file(path, content)
            streamlit.rerun()

    streamlit.subheader(f"📄 {path}")

    if not doc:
        streamlit.info("Generando documentación...")
        return

    streamlit.markdown(doc)

    # Nombre del archivo de descarga
    file_to_donwload = Path(path).stem
    streamlit.download_button(
        label="⬇️ Descargar como Markdown",
        data=doc,
        file_name=f"{file_to_donwload}_doc.md",
        mime="text/markdown",
    )

#Caso de que se suba un unico fichero
def _render_uploaded_file_documentation() -> None:
    from services import chat_service
    uploaded = state_service.get_uploaded_file()
    if not uploaded:
        return

    name, content = uploaded
    doc = state_service.get_last_documentation()

    col1, _ = streamlit.columns([8, 18])
    with col1:
        if streamlit.button("💬 Preguntar al Agente de IA", use_container_width=True, type="primary"):
            chat_service.start_chat_with_file(name, content)
            streamlit.rerun()

    streamlit.subheader(f"📄 {name}")

    if not doc:
        streamlit.info("Generando documentación...")
        return

    streamlit.markdown(doc)

    # Nombre del archivo para descarga
    stem = Path(name).stem
    streamlit.download_button(
        label="⬇️ Descargar como Markdown",
        data=doc,
        file_name=f"{stem}_doc.md",
        mime="text/markdown",
    )

def _render_result() -> None:
    if state_service.get_selected_file():
        _render_file_documentation()
        return

    project = state_service.get_current_project()
    if project:
        tree = doc_service.get_project_tree()
        _render_tree(tree)
        return

    if state_service.get_uploaded_file():
        _render_uploaded_file_documentation()
        return

def render_documentation() -> None:
    _render_header()
    _render_uploader()
    _render_result()