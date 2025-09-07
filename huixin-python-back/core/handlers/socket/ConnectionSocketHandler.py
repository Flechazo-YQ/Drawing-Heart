import flask, logging

from core.states.SocketState import SocketState

class ConnectionSocketHandler:

    # 处理客户端断开连接
    @staticmethod
    @SocketState.socketio.on(SocketState.DISCONNECT)
    def disconnect():
        sid = flask.request.sid # type: ignore

        if (not sid): return None

        userId = SocketState.sidToUserId.pop(sid, None)
        adminId = SocketState.sidToAdminId.pop(sid, None)

        if (userId): 
            SocketState.userIdToSid.pop(userId, None)
            logging.info(f'用户{ userId }(SID: { sid })已断开连接')
            return None

        if (adminId): 
            SocketState.adminIdToSid.pop(adminId, None)
            logging.info(f'管理员{ adminId }(SID: { sid })已断开连接')
            return None

        logging.warning(f'⚠️ 未认证的客户端断开连接: { sid }')
        return None
