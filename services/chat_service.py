from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import streamlit
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from agent.graph import build_graph
from ui import app_ui, chat_ui
from services import state_service, doc_service
from repositories import conversation_repo as conv_repo

# Recompila el grafo una unica vez por ejecución de la app, y lo guarda en caché para no volver a compilarlo en cada interacción.
@streamlit.cache_resource
def get_graph():
    conn = sqlite3.connect("data/app.db", check_same_thread = False)
    memory = SqliteSaver(conn)

    return build_graph(checkpointer_sqlite_saver = memory)

def _build_conversation_title(user_input: str, chat_from_file: str) -> str:
    if chat_from_file:
        return f"📄 {Path(chat_from_file[0]).name}"
    return user_input


def _create_conversation(thread_id: str, user_input: str) -> None:
    chat_from_file = state_service.get_chat_file()
    file_path = chat_from_file[0] if chat_from_file else None
    title = _build_conversation_title(user_input, chat_from_file)
    conv_repo.create_conversations(thread_id, title, file_path=file_path)


def _update_conversation_title(thread_id: str, user_input: str) -> None:
    chat_from_file = state_service.get_chat_file()
    file_path = chat_from_file[0] if chat_from_file else None
    title = _build_conversation_title(user_input, chat_from_file)
    conv_repo.update_conversation_title_and_file(thread_id, title, file_path)

def _send_messages_to_agent():
    graph = get_graph()

    chat_from_file = state_service.get_chat_file()
    context = chat_from_file[1] if chat_from_file else ""

    return graph.stream(
        {
            "messages": state_service.get_last_user_message(),
            "context": context
        },
            config={"configurable": {"thread_id": state_service.get_thread_id()}},
            stream_mode="values")

# Intenta recuperar el fichero de un chat en caso de que exista para actualizar el contexto del Agente
def _restore_chat_context(thread_id: str) -> None:
    conv = conv_repo.get_conversation(thread_id)

    if not conv or not conv.get("file_path"):
        state_service.clear_chat_file()
        return

    file_path = conv["file_path"]

    # Si no hay proyecto cargado en la sesion, no podemos leer el archivo, se solucionara cuando se implemente persistencia de datos en BBDD de los proyectos
    project = state_service.get_current_project()
    if not project:
        state_service.clear_chat_file()
        return

    # Intentar leer el archivo desde el proyecto
    project_path, _ = project
    try:
        content = doc_service.read_file_from_project(project_path, file_path)
        state_service.set_chat_file(file_path, content)
    except FileNotFoundError:
        state_service.clear_chat_file()

def init():
    handle_input()

def handle_input() -> None:
    new_conversation: bool = False

    #Comprueba si hay input
    user_input = chat_ui.get_user_input()
    if not user_input:
        return

    thread_id = state_service.get_thread_id()

    # Comprobamos que exista la conversacion en caso contrario la creamos
    if not conv_repo.exists_conversation(thread_id):
        _create_conversation(thread_id, user_input)
    #Actualizamos el titulo de la conversacion en BBDD cuando se mande el primer mensaje del user, en el caso de que si existiera la conversacion, solo para chat normal
    elif conv_repo.is_new_conversation(thread_id):
        _update_conversation_title(thread_id, user_input)

    #almacenamos el mensaje del usuario
    state_service.add_message(HumanMessage(content = user_input))
    chat_ui.render_user_message(user_input)

    #Llamamos al agente con el historial y devuelve un stream de eventos con la respuesta
    stream = _send_messages_to_agent()
    full_response = chat_ui.render_streaming_response(stream)
    state_service.add_message(AIMessage(content = full_response))

    conv_repo.increment_message_count(thread_id)
    if new_conversation:
        streamlit.rerun()

def start_chat_with_file(file_path: str, content: str) -> None:
    state_service.new_thread_id()
    thread_id = state_service.get_thread_id()
    state_service.clear()

    state_service.set_chat_file(file_path, content)
    title = f"📄 {Path(file_path).name}"
    conv_repo.create_conversations(thread_id, title, file_path=file_path)

    state_service.set_screen_type(1)




def list_conversations() -> list[dict]:
    return conv_repo.list_all_conversations()

#Cargamos los mensajes de x thread_id almacenados por el grafo en la propia BBDD de Langraph
def load_messages(thread_id: str) -> list[BaseMessage]:
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.get_state(config)

    messages = state.values.get("messages", [])
    filtered_messages = []
    for m in messages:
        if isinstance(m, (HumanMessage, AIMessage)):
            filtered_messages.append(m)
    
    return filtered_messages

#Seteamos nuevo id y rellenamos la lista de session_state con los mensajes de x conversacion
def switch_conversation(thread_id: str) -> None:
    state_service.set_thread_id(thread_id)
    state_service.clear()

    for msg in load_messages(thread_id):
        state_service.add_message(msg)

    _restore_chat_context(thread_id)

def delete_conversation(thread_id: str):
    conv_repo.delete_conversation(thread_id)