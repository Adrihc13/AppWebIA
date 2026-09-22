import streamlit

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from services import state_service
from agent.llm import MODEL_NAME

streamlit.markdown(
    """
    <style>
    div[data-testid="stButton"] > button {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def _render_chatbot_header():
    streamlit.title("Buenas soy la Rana inteligente Grog 🐸, pregunta lo que quieras!")
    streamlit.caption("Chatbot con memoria de conversación · LangGraph + Groq")
    

def _render_chatbot_sidebar():
    with streamlit.sidebar:
        streamlit.header("Opciones")

        # De momento borra el historial
        if streamlit.button("🗑️ Nueva conversación"):    
            state_service.new_conversation()
            streamlit.rerun()

        """
        # Elimina los 2 ultimos mensajes
                if streamlit.button("Borrar ultimo mensaje") and streamlit.session_state.messages:
                    state_service.remove_last_exchange()
                    streamlit.rerun()
        """
        
        streamlit.divider()
        streamlit.subheader("Conversaciones")
        _render_conversation_list()

        streamlit.divider()
        streamlit.divider()
        streamlit.caption(f"Modelo: `{MODEL_NAME}`")
        streamlit.caption(f"Mensajes: {len(state_service.get_messages())}")

def _render_chatbot_history():
    for msg in state_service.get_messages():
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            with streamlit.chat_message(role):
                streamlit.markdown(msg.content)

def _render_conversation_list():
    from services import chat_service
    conversations = chat_service.list_conversations()

    if not conversations:
        streamlit.caption("Cree una nueva conversación o escriba por el chat para comenzar")
        return

    actual_thread_id = state_service.get_thread_id()

    for c in conversations:
        tid = c["thread_id"]
        title = c["title"]
        mark = "●" if tid == actual_thread_id else "○"

        col1, col2 = streamlit.columns([4,1])

        with col1: 
            if streamlit.button(f"{mark} {title}", key = f"conv_{tid}", use_container_width = True) and tid != actual_thread_id:
                chat_service.switch_conversation(tid)
                streamlit.rerun()
        with col2:
            if streamlit.button("🗑️", key = f"del_{tid}"):
                chat_service.delete_conversation(tid)
                streamlit.rerun()

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
    _render_chatbot_history()
    _render_chatbot_sidebar()