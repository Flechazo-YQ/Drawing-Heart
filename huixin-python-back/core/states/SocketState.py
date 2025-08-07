import queue, logging, time

from flask_socketio import SocketIO

class SocketState:
    socketio = SocketIO()
    socketioTaskQueue = queue.Queue()