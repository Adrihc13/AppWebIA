from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Config del modelo
#MODEL_NAME = "groq/compound-mini"
MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "Eres un asistente útil, claro y conciso. "
    "Respondes en el idioma del usuario. "
    "Si no sabes algo, lo dices con honestidad."
)

CONTEXT_PROMPT = (
    "A continuación tienes el contenido de un fichero de código "
    "sobre el que el usuario está preguntando. Úsalo como contexto "
    "para responder sus dudas:"
)

load_dotenv()

def create_llm(temperature_value = 0.7):
    return ChatGroq(model = MODEL_NAME, temperature = temperature_value)

def build_system_prompt(context: str = ""):
    if not context:
        return SYSTEM_PROMPT

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{CONTEXT_PROMPT}\n\n"
        f"```\n{context}\n```"
    )