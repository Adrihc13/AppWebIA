from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from agent.llm import create_llm  

class DocState(TypedDict):
    code: str
    filename: str
    documentation:str

def _build_prompt(code: str, filename: str) -> str:
    return f'''Eres un experto en Python. Analiza el siguiente archivo 
y genera documentación técnica clara y concisa en formato Markdown.

## Instrucciones
- Empieza con un resumen general del propósito del archivo.
- Lista las clases principales con su propósito.
- Lista las funciones/métodos principales con su funcionalidad.
- Indica las dependencias externas (imports de librerías no estándar).
- Si hay algo relevante (patrones de diseño, notas técnicas), añádelo.
- Responde en Castellano.

## Archivo: {filename}
```python
{code}
```

## Documentación
'''

def analyze_code(state: DocState) -> dict:
    llm = create_llm(temperature_value = 0.2)
    promt = _build_prompt(state["code"], state["filename"])
    response = llm.invoke(promt)
    return {"documentation": response.content}

def build_graph():
    graph_builder = StateGraph(DocState)
    graph_builder.add_node("analyze", analyze_code)
    graph_builder.add_edge(START, "analyze")
    graph_builder.add_edge("analyze", END)
    return graph_builder.compile()
