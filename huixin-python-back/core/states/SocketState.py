from core.states.GlobalState import GlobalState

from flask_socketio import SocketIO

class SocketState:
    SOCKETIO = SocketIO(
        GlobalState.APP,
        cors_allowed_origins = "*",
        async_mode = 'threading',
        logger = True,
        engineio_logger = True
    )
