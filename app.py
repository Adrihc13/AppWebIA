"""Interfaz Streamlit del agente conversacional."""

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from agent.graph import build_graph
from agent.graph import build_graph, MODEL_NAME

# --- Configuración de la página ---
st.set_page_config(page_title="Mi Agente IA", page_icon="🤖", layout="centered")
st.title("Buenas soy la Rana inteligente Grog 🐸, pregunta lo que quieras!")
st.caption("Chatbot con memoria de conversación · LangGraph + Groq")

# --- Construir el grafo una sola vez por sesión ---
# @st.cache_resource evita recompilar el grafo en cada re-ejecución de Streamlit.
@st.cache_resource
def get_graph():
    return build_graph()


graph = get_graph()

# --- Estado del historial en la sesión de Streamlit ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar con botón de reset ---
with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Modelo: `{MODEL_NAME}`")
    st.caption(f"Mensajes: {len(st.session_state.messages)}")

# --- Pintar el historial existente ---
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- Input del usuario ---
if prompt := st.chat_input("Escribe tu mensaje..."):
    # 1. Mostrar mensaje del usuario
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Invocar al agente y hacer streaming de la respuesta
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # .stream() emite eventos por cada token del LLM
        for event in graph.stream(
            {"messages": st.session_state.messages},
            stream_mode="values",
        ):
            last = event["messages"][-1]
            if isinstance(last, AIMessage):
                full_response = last.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    # 3. Guardar la respuesta en el historial
    st.session_state.messages.append(AIMessage(content=full_response))
