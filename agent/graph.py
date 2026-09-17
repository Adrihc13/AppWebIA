"""Definición del agente conversacional con LangGraph."""

import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()

# --- Configuración del modelo ---
MODEL_NAME = "groq/compound-mini"  # rápido y potente en Groq

SYSTEM_PROMPT = (
    "Eres un asistente útil, claro y conciso. "
    "Respondes en el idioma del usuario. "
    "Si no sabes algo, lo dices con honestidad."
    "Si te preguntan tu nombre te identificas como 'Grog, la rana inteligente'."
    "Al responder, incluye 'Grog piensa' o 'Grog cree' y despues añades tu respuesta, a no ser que te pregunte por tu nombre, en cuyo caso solo dices tu nombre."
)


# --- Estado del grafo ---
class AgentState(TypedDict):
    """Estado que viaja entre nodos.

    'messages' es una lista de mensajes. El reducer 'add_messages' se encarga
    de añadir los mensajes nuevos a la lista existente en lugar de
    sobrescribirla (esto es lo que permite la memoria de la conversación).
    """
    messages: Annotated[list[BaseMessage], add_messages]


# --- Nodo del LLM ---
def call_model(state: AgentState) -> dict:
    """Llama al LLM con el historial completo de mensajes."""
    llm = ChatGroq(model=MODEL_NAME, temperature=0.7)

    # Nos aseguramos de que el primer mensaje sea el system prompt
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]

    response = llm.invoke(messages)
    return {"messages": [response]}


# --- Construcción del grafo ---
def build_graph():
    """Crea y compila el grafo del agente."""
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("model", call_model)

    graph_builder.add_edge(START, "model")
    graph_builder.add_edge("model", END)

    return graph_builder.compile()