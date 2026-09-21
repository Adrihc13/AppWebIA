
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import streamlit
from agent.graph import build_graph
from ui import app_ui, chat_ui
from services import state_service

# Recompila el grafo una unica vez por ejecución de la app, y lo guarda en caché para no volver a compilarlo en cada interacción.
@streamlit.cache_resource
def get_graph():
    return build_graph()

def init():
    handle_input()

def handle_input() -> None:
    #Comprueba si hay input
    user_input = chat_ui.get_user_input()
    if not user_input:
        return

    #alamacenamos el mensaje del usuario
    state_service.add_message(HumanMessage(content = user_input))
    chat_ui.render_user_message(user_input)

    #Llamamos al agente con el historial y devuelve un stream de eventos con la respuesta
    stream = _send_messages_to_agent()
    full_response = chat_ui.render_streaming_response(stream)
    state_service.add_message(AIMessage(content = full_response))


def _send_messages_to_agent():
    graph = get_graph()
    return graph.stream(
        {"messages": state_service.get_messages()}, stream_mode="values")

