import streamlit
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

def _render_result() -> None:
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