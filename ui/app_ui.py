import streamlit
from services import state_service
from ui import chat_ui, doc_ui

def paint_screen():
    streamlit.set_page_config(page_title="Doc Generator AI Agent", page_icon="🤖", layout="centered")

    col1, col2, col3 = streamlit.columns([1,1,3])

    with col1:
        if streamlit.button("Chat"):
            state_service.set_screen_type(1)

    with col2:
        if streamlit.button("Doc Generator"):
            state_service.set_screen_type(2)

    screen_type = state_service.get_screen_type()
    if screen_type == 1:
        chat_ui.render_chatbot()
    elif screen_type == 2:
        doc_ui.render_documentation()


