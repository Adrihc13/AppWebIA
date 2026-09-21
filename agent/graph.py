from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langchain_core.messages import SystemMessage

from .agent_state import AgentState
from .llm import MODEL_NAME, SYSTEM_PROMPT


# Llamada al LLM
def call_model(state: AgentState) -> dict:
    llm = ChatGroq(model=MODEL_NAME, temperature=0.7)

    # Nos aseguramos de que el primer mensaje sea el system prompt
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]

    response = llm.invoke(messages)
    return {"messages": [response]}


# Creacion y compilacion del grafo
def build_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("model", call_model)

    graph_builder.add_edge(START, "model")
    graph_builder.add_edge("model", END)

    return graph_builder.compile()