"""Interfaz Streamlit del agente conversacional."""

import streamlit
from langchain_core.messages import AIMessage, HumanMessage
from agent.graph import build_graph, MODEL_NAME

# --- Configuración de la página ---
streamlit.set_page_config(page_title="Test Web AI", page_icon="🤖", layout="centered")


# --- Definicion de funciones ---
# Recompila el grafo una unica vez por ejecución de la app, y lo guarda en caché para no volver a compilarlo en cada interacción.
@streamlit.cache_resource
def get_graph():
    return build_graph()

def paint_home():
    streamlit.title("APP - WIP")
    streamlit.caption("working in progress...")

def paint_chatbot():
    streamlit.title("Buenas soy la Rana inteligente Grog 🐸, pregunta lo que quieras!")
    streamlit.caption("Chatbot con memoria de conversación · LangGraph + Groq")

    if "messages" not in streamlit.session_state:
        streamlit.session_state.messages = []

    # --- Sidebar con botón de reset ---
    with streamlit.sidebar:
        streamlit.header("Opciones")
        if streamlit.button("🗑️ Nueva conversación"):
            streamlit.session_state.messages = []
            streamlit.rerun()

        #Elimina los 2 ultimos mensajes
        if streamlit.button("Borrar ultimo mensaje") and streamlit.session_state.messages:
            streamlit.session_state.messages = streamlit.session_state.messages[:-2] 
            streamlit.rerun()

        streamlit.divider()
        streamlit.caption(f"Modelo: `{MODEL_NAME}`")
        streamlit.caption(f"Mensajes: {len(streamlit.session_state.messages)}")

    # --- Pintar el historial existente ---
    for msg in streamlit.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with streamlit.chat_message(role):
            streamlit.markdown(msg.content)

    # --- Input del usuario ---
    if prompt := streamlit.chat_input("Escribe tu mensaje..."):
        # 1. Mostrar mensaje del usuario
        user_msg = HumanMessage(content=prompt)
        streamlit.session_state.messages.append(user_msg)
        with streamlit.chat_message("user"):
            streamlit.markdown(prompt)

        # 2. Invocar al agente y hacer streaming de la respuesta
        with streamlit.chat_message("assistant"):
            placeholder = streamlit.empty()
            full_response = ""

            # .stream() emite eventos por cada token del LLM
            for event in graph.stream(
                {"messages": streamlit.session_state.messages},
                stream_mode="values",
            ):
                last = event["messages"][-1]
                if isinstance(last, AIMessage):
                    full_response = last.content
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        # 3. Guardar la respuesta en el historial
        streamlit.session_state.messages.append(AIMessage(content=full_response))


def paint_screen():
    if "screen_type" not in streamlit.session_state:
        streamlit.session_state.screen_type = 0

    if streamlit.button("Chat Bot"):
        streamlit.session_state.screen_type = 1

    if streamlit.button("App"):
            streamlit.session_state.screen_type = 2
        

    if streamlit.session_state.screen_type == 1:
        paint_chatbot()
    elif streamlit.session_state.screen_type == 2:
        paint_home()
    

# --- Ejecucion en cada interaccion ---
graph = get_graph()

paint_screen()


