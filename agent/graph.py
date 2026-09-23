from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from .agent_state import AgentState
from .llm import MODEL_NAME, SYSTEM_PROMPT, create_llm, build_system_prompt


# Llamada al LLM
def call_model(state: AgentState) -> dict:
    llm = create_llm()

    messages = state["messages"]
    context = state.get("context", "") or "" #para que no devuelva None en caso de que exista la clave pero sin valor

    #Ampliamos el contexto del system prompt para el caso de que haya un fichero de codigo a preguntar
    system_content = build_system_prompt(context = context)

    # Filtramos el historial de mensajes y eliminamos mensajes del systema/prompts para insertarle despues el nuevo prompt con el contexto actualizado
    conversation = []
    for m in messages:
        if not isinstance(m,SystemMessage):
            conversation.append(m)

    full_messages = [SystemMessage(content=system_content), *conversation]

    response = llm.invoke(full_messages)
    return {"messages": [response]}


# Creacion y compilacion del grafo
def build_graph(checkpointer_sqlite_saver = None):
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("model", call_model)

    graph_builder.add_edge(START, "model")
    graph_builder.add_edge("model", END)

    return graph_builder.compile(checkpointer=checkpointer_sqlite_saver)