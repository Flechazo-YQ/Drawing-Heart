import queue

from flask_socketio import SocketIO

class SocketState:
    socketio = SocketIO()
    socketioTaskQueue = queue.Queue()

    sidToUserId = {}
    userIdToSid = {}

    sidToAdminId = {}
    adminIdToSid = {}