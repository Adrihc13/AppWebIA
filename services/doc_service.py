import streamlit
from agent import doc_graph
from services import state_service

MAX_FILE_SIZE = 50_000  #Bytes
MAX_FILE_SIZE_MB = 0.05 #MB


@streamlit.cache_resource
def _get_graph():
    return doc_graph.build_graph()

def _read_file(file) -> str:
    return file.read().decode("utf-8")

def handle_upload(file) -> None:
    if file is None:
        return

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