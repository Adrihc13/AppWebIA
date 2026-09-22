import uuid

import streamlit
from langchain_core.messages import BaseMessage, HumanMessage
from repositories import db, conversation_repo

# --- Inits ---
def init() -> None:
    db.init_db()
    _init_messages()
    _init_screens()
    _init_documentation()

def _init_screens():
    if "screen_type" not in streamlit.session_state:
        streamlit.session_state.screen_type = 0
    
def _init_messages() -> None:
    if "messages" not in streamlit.session_state:
            streamlit.session_state.messages = []

def _init_documentation() -> None:
    if "last_documentation"not in streamlit.session_state:
        streamlit.session_state.last_documentation = ""

# --- Message ---
def add_message(msg: BaseMessage) -> None:
    streamlit.session_state.messages.append(msg)

def get_messages() -> list[BaseMessage]:
    return streamlit.session_state.messages

def get_last_user_message() -> HumanMessage | None:
    messages = get_messages()
    if not messages:
        return None

    last_message = messages[-1]
    if isinstance(last_message, HumanMessage):
        return last_message
    return None 


def clear()-> None:
    streamlit.session_state.messages = []

def new_conversation() -> None:
    new_thread_id()
    clear()
    conversation_repo.create_conversations(streamlit.session_state.thread_id, "Nueva conversación")

# Elimina los 2 ultimos mensajes, la pregunta del usuario y la respuesta de la IA
def remove_last_exchange() -> None:
    if len(streamlit.session_state.messages) >= 2:
        streamlit.session_state.messages = streamlit.session_state.messages[:-2] 

def get_thread_id() -> str:
    if "thread_id" not in streamlit.session_state:
        new_thread_id()
    return streamlit.session_state.thread_id

def set_thread_id(thread_id: str) -> None:
    streamlit.session_state.thread_id = thread_id

def new_thread_id() -> None:
    streamlit.session_state.thread_id = str(uuid.uuid4())

# --- Screen ---
def get_screen_type() -> int:
    return streamlit.session_state.screen_type

def set_screen_type(screen_type: int) -> None:
    streamlit.session_state.screen_type = screen_type

# --- Documentation ---
def get_last_documentation() -> str:
    return streamlit.session_state.get("last_documentation","")

def set_last_documentation(new_doc: str) -> None:
    streamlit.session_state.last_documentation = new_doc

def clear_last_documentation() -> str:
    streamlit.session_state.last_documentation = ""