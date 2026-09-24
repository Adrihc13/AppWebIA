# 🤖 Doc Generator & Chatbot

Aplicación web con dos herramientas basadas en IA:
- **💬 Chatbot** — conversación con memoria y contexto
- **📄 Documentador** — genera documentación de archivos Python o proyectos completos (`.zip`)
  y permite preguntar al agente sobre cualquier archivo del proyecto.

Construida con **LangGraph**, **Groq** y **Streamlit**.

## 🌐 Demo online

👉 **[doc-generator-and-chatbot.streamlit.app](https://doc-generator-and-chatbot.streamlit.app)**

⚠️ **Nota sobre la demo**: el almacenamiento de la versión gratuita de Streamlit Cloud
es efímero — la base de datos se reinicia cada ~24h o al reiniciar la app. Para uso
continuado con persistencia real, clona el repo e instala en local.

## ✨ Características

### Chatbot
- Conversación con memoria persistente entre mensajes
- Múltiples conversaciones en paralelo (sidebar)
- Títulos automáticos desde el primer mensaje
- Posibilidad de preguntar sobre un archivo concreto (chat contextual)

### Documentador de código
- Subida de archivos `.py` individuales
- Subida de proyectos completos en `.zip` con validación de seguridad
- Árbol interactivo del proyecto (solo archivos `.py` y `.sql`)
- Documentación técnica generada automáticamente
- Chat contextual por archivo seleccionado

## 🛠️ Stack

- **Python 3.14**
- **LangGraph** — orquestación del agente
- **Groq** — LLM (modelo por defecto: `openai/gpt-oss-20b`)
- **Streamlit** — interfaz web
- **SQLite** — persistencia de conversaciones y estado

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura en capas**:
- **`agent/`** — Lógica del agente: grafo LangGraph, prompts, configuración del LLM
- **`services/`** — Orquestación de los flujos de la aplicación
- **`ui/`** — Componentes visuales y gestión de la interacción
- **`repositories/`** — Acceso a datos (SQLite)