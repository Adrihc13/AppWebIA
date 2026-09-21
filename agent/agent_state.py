from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# Clase que contine una lista de mensajes la cual se le añaden los mensajes de una conversacion.
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]