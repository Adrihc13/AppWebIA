
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import streamlit
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from agent.graph import build_graph
from ui import app_ui, chat_ui
from services import state_service
from repositories import conversation_repo as conv_repo

# Recompila el grafo una unica vez por ejecución de la app, y lo guarda en caché para no volver a compilarlo en cada interacción.
@streamlit.cache_resource
def get_graph():
    conn = sqlite3.connect("data/app.db", check_same_thread = False)
    memory = SqliteSaver(conn)

    return build_graph(checkpointer_sqlite_saver = memory)

def init():
    handle_input()

def handle_input() -> None:
    #Comprueba si hay input
    user_input = chat_ui.get_user_input()
    if not user_input:
        return

    thread_id = state_service.get_thread_id()

    #creamos conversación en caso de que no exista
    if not conv_repo.exists_conversation(thread_id):
        conv_repo.create_conversations(thread_id, user_input)

    #almacenamos el mensaje del usuario
    state_service.add_message(HumanMessage(content = user_input))
    chat_ui.render_user_message(user_input)

    #Llamamos al agente con el historial y devuelve un stream de eventos con la respuesta
    stream = _send_messages_to_agent()
    full_response = chat_ui.render_streaming_response(stream)
    state_service.add_message(AIMessage(content = full_response))

    conv_repo.increment_message_count(thread_id)


def _send_messages_to_agent():
    graph = get_graph()
    return graph.stream(
        {"messages": state_service.get_last_user_message()},
            config={"configurable": {"thread_id": state_service.get_thread_id()}},
            stream_mode="values")

