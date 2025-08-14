import flask, logging

from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState

class ConnectionSocketHandler:

    @staticmethod
    @SocketState.socketio.on('connect')
    def handleConnect():
        sid = flask.request.sid # type: ignore

        logging.info(f"客户端连接成功: { sid }")

    @staticmethod
    @SocketState.socketio.on('disconnect')
    def handleDisconnect():
        sid = flask.request.sid # type: ignore

        if (not sid): return

        userId = SocketState.sidToUserId.pop(sid, None)

        if (userId): 
            SocketState.userIdToSid.pop(userId, None)
            logging.info(f"用户断开连接: { userId }")
            return

        adminId = SocketState.sidToAdminId.pop(sid, None)

        if (adminId): 
            SocketState.adminIdToSid.pop(adminId, None)
            logging.info(f"管理员断开连接: { adminId }")
            return

        logging.warning(f"⚠️ 未认证的客户端断开连接: { sid }")

