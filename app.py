from ui import app_ui
from services import state_service, chat_service


def init():
    # Inicializamos el estado de la app (este inicializa las variables de session_state de streamlit)
    state_service.init()

    # llamamos a la capa de UI para el pintado
    app_ui.paint_screen()


    if state_service.get_screen_type() == 1:
        chat_service.init()
        #pass

init()