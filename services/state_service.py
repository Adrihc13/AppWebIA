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
    _init_project()

def _init_screens():
    if "screen_type" not in streamlit.session_state:
        streamlit.session_state.screen_type = 0
    
def _init_messages() -> None:
    if "messages" not in streamlit.session_state:
            streamlit.session_state.messages = []

def _init_documentation() -> None:
    if "last_documentation"not in streamlit.session_state:
        streamlit.session_state.last_documentation = ""

def _init_project() -> None:
    if "current_project_path"not in streamlit.session_state:
        streamlit.session_state.current_project_path = None
    if "current_project_name"not in streamlit.session_state:
        streamlit.session_state.current_project_name = None
    if "selected_file_path" not in streamlit.session_state:
        streamlit.session_state.selected_file_path = None
    if "selected_file_content" not in streamlit.session_state:
        streamlit.session_state.selected_file_content = None

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

# --- Project ---
def get_current_project() -> tuple[str, str] | None:
    path = streamlit.session_state.current_project_path
    name = streamlit.session_state.current_project_name

    if path and name:
        return path, name
    return None

def set_current_project(path: str, name: str) -> None:
    streamlit.session_state.current_project_path = path
    streamlit.session_state.current_project_name = name

def clear_current_project() -> None:
    streamlit.session_state.current_project_path = None
    streamlit.session_state.current_project_name = None

def set_selected_file(path: str, content: str) -> None:
    streamlit.session_state.selected_file_path = path
    streamlit.session_state.selected_file_content = content

def get_selected_file() -> tuple[str, str] | None:
    path = streamlit.session_state.get("selected_file_path")
    content = streamlit.session_state.get("selected_file_content")
    if path and content:
        return path, content
    return None

def clear_selected_file() -> None:
    streamlit.session_state.selected_file_path = None
    streamlit.session_state.selected_file_content = None