import flask, logging

from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState

class ConnectionSocketHandler:

    @staticmethod
    @SocketState.socketio.on('connect')
    def handleConnect():
        logging.info('Client connected')

    @staticmethod
    @SocketState.socketio.on('disconnect')
    def handleDisconnect():
        logging.info('Client disconnected')

        #如果是管理员断开连接，更新状态
        sid = flask.request.sid # type: ignore

        adminId = GlobalState.sidToAdminId.pop(sid, None)

        logging.info(f'Admin { adminId } disconnected') if (adminId) else logging.info('Admin not found')