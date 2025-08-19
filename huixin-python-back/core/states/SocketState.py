from queue import Queue
from flask_socketio import SocketIO

class SocketState:
    socketio = SocketIO()
    socketioTaskQueue = Queue()

    sidToUserId = {}
    userIdToSid = {}

    sidToAdminId = {}
    adminIdToSid = {}