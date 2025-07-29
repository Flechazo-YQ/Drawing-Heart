from flask_socketio import SocketIO
from handlers.ChatHandler import ChatHandler

class SocketState:
    socketio = SocketIO(
        ChatHandler.app, 
        cors_allowed_origins = "*", 
        async_mode = 'threading', 
        logger = True, 
        engineio_logger = True
    )
