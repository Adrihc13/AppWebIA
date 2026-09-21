import streamlit
from langchain_core.messages import BaseMessage

def init() -> None:
    _init_messages()
    _init_screens()

def _init_screens():
    if "screen_type" not in streamlit.session_state:
        streamlit.session_state.screen_type = 0
    
def _init_messages() -> None:
    if "messages" not in streamlit.session_state:
            streamlit.session_state.messages = []

# --- Message ---
def add_message(msg: BaseMessage) -> None:
    streamlit.session_state.messages.append(msg)

def get_messages() -> list[BaseMessage]:
    return streamlit.session_state.messages

def clear()-> None:
    streamlit.session_state.messages = []

# Elimina los 2 ultimos mensajes, la pregunta del usuario y la respuesta de la IA
def remove_last_exchange() -> None:
    if len(streamlit.session_state.messages) >= 2:
        streamlit.session_state.messages = streamlit.session_state.messages[:-2] 

# --- Screen ---
def get_screen_type() -> int:
    return streamlit.session_state.screen_type

def set_screen_type(screen_type: int) -> None:
    streamlit.session_state.screen_type = screen_type