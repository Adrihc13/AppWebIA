import streamlit
from pathlib import Path
from services import doc_service, state_service

def _render_header() -> None:
    streamlit.title("📄 Documentador de código")
    streamlit.caption("Sube un archivo Python y obtén documentación técnica generada por un Agente de IA")

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

def _render_file_documentation() -> None:
    selected = state_service.get_selected_file()
    if not selected:
        return

    path, _ = selected
    doc = state_service.get_last_documentation()

    # Botón de volver
    col1, _ = streamlit.columns([2, 8])
    with col1:
        if streamlit.button("← Volver al árbol", use_container_width=True):
            state_service.clear_selected_file()
            state_service.clear_last_documentation()
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

def _render_result() -> None:
    if state_service.get_selected_file():
        _render_file_documentation()
        return

    project = state_service.get_current_project()
    if project:
        tree = doc_service.get_project_tree()
        _render_tree(tree)
        return

    doc = state_service.get_last_documentation()
    if not doc:
        return

    streamlit.divider()
    streamlit.subheader("Resultado")
    streamlit.markdown(doc)

    streamlit.download_button(
        label="⬇️ Descargar como Markdown",
        data=doc,
        file_name="documentation.md",
        mime="text/markdown",
    )

def render_documentation() -> None:
    _render_header()
    _render_uploader()
    _render_result()