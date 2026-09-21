import streamlit

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from services import state_service
from agent.llm import MODEL_NAME


def _render_chatbot_header():
    streamlit.title("Buenas soy la Rana inteligente Grog 🐸, pregunta lo que quieras!")
    streamlit.caption("Chatbot con memoria de conversación · LangGraph + Groq")
    

def _render_chatbot_sidebar():
    with streamlit.sidebar:
        streamlit.header("Opciones")

        # De momento borra el historial
        if streamlit.button("🗑️ Nueva conversación"):    
            state_service.clear()
            streamlit.rerun()

        # Elimina los 2 ultimos mensajes
        if streamlit.button("Borrar ultimo mensaje") and streamlit.session_state.messages:
            state_service.remove_last_exchange()
            streamlit.rerun()

        streamlit.divider()
        streamlit.caption(f"Modelo: `{MODEL_NAME}`")
        streamlit.caption(f"Mensajes: {len(state_service.get_messages())}")

def _render_chatbot_history():
    for msg in state_service.get_messages():
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            with streamlit.chat_message(role):
                streamlit.markdown(msg.content)

def render_user_message(text: str):
    with streamlit.chat_message("user"):
        streamlit.markdown(text)
    
def render_streaming_response(stream) -> str:
    with streamlit.chat_message("assistant"):
        placeholder = streamlit.empty() # Burbuja donde ira la respuesta del asistente
        full_response = "" # variable que contendra la respuesta completa

        for event in stream:
            last = event["messages"][-1]
            if isinstance(last, AIMessage):
                full_response = last.content
                placeholder.markdown(full_response + " ...")
    
    placeholder.markdown(full_response)
    return full_response

def get_user_input():
    return streamlit.chat_input("Escribe tu mensaje...")

def render_chatbot():
    _render_chatbot_header()
    _render_chatbot_sidebar()
    _render_chatbot_history()