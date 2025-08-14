import flask, flask_socketio, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler

from typing import Dict

class UserSocketHandler:

    # 处理用户的认证请求
    @staticmethod
    @SocketState.socketio.on("user_auth")
    def handleUserAuth(data: Dict):
        sid = flask.request.sid # type: ignore
        token = data.get("token")

        if (not sid): return
        if (not token): 
            SocketQueueHandler.queueEmit("auth_error", {
                "message": "Token is missing"
            }, room=sid)
            return
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId or not MongoDBConfig.userManager.getUserById(userId)):
            SocketQueueHandler.queueEmit("auth_error", {
                "message": "Invalid token or user not found"
            }, room=sid)
            return

        SocketState.sidToUserId[sid] = userId
        SocketState.userIdToSid[userId] = sid

        flask_socketio.join_room(sid, room=f"user_{ userId }") # type: ignore
        SocketQueueHandler.queueEmit("auth_success", {
            "message": "认证成功, 连接已建立"
        }, room=sid)
        logging.info(f"用户{ userId }(SID: { sid })已认证成功并加入房间")

    # 处理用户发送的消息
    @staticmethod
    @SocketState.socketio.on("user_message")
    def handleUserMessage(data: Dict):
        sid = flask.request.sid # type: ignore

        if (not sid): return

        userId = SocketState.sidToUserId.get(sid)

        if (not userId): 
            SocketQueueHandler.queueEmit("message_error", {
                "message": "User not authenticated"
            }, room=sid)
            return
        
        chatId = data.get("chatId")
        content = data.get("content")

        if (not chatId or not content):
            SocketQueueHandler.queueEmit("message_error", {
                "message": "Missing Chat ID and content"
            }, room=sid)
            return

        # 处理用户消息
        messageId = MongoDBConfig.messageManager.createMessage(
            chatId=chatId,
            type="text",
            content=content,
            sender="user"
        )

        if (not messageId):
            SocketQueueHandler.queueEmit("message_error", {
                "message": "Failed to create message"
            }, room=sid)
            return

        (label, _) = GlobalState.CLASSIFIER.predict(content) if (GlobalState.CLASSIFIER) else (None, None)

        if (label != "危险"): return

        chat = MongoDBConfig.chatManager.getChatById(chatId)

        if (not chat): return

        adminId = chat.get("adminId")
        user = MongoDBConfig.userManager.getUserById(userId)
        username = user.get("username") if (user) else "未知用户"

        alertData = {
            "chatId": chatId,
            "userId": userId,
            "username": username,
            "content": content
        }

        if (not adminId):
            SocketQueueHandler.queueEmit("danger_alert", alertData, room="admin_room")
            logging.info(f"用户{ username }({ userId })在对话{ chatId }中发送了危险消息，已通知管理员")
            return

        adminSid = SocketState.adminIdToSid.get(adminId)

        if (not adminSid): return

        SocketQueueHandler.queueEmit("danger_alert", alertData, room=adminSid)
        logging.info(f"用户{ username }({ userId })在对话{ chatId }中发送了危险消息，已通知管理员{ adminId }")
