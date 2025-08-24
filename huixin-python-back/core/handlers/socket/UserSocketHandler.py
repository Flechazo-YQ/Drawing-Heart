import flask, flask_socketio, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.utils.AuthenticateHelper import AuthenticateHelper
from core.utils.BroadcastHelper import BroadcastHelper

from typing import Dict

class UserSocketHandler:

    # 处理用户的认证请求
    @staticmethod
    @SocketState.socketio.on("user_auth")
    @UserTokenHandler.userTokenRequired
    def handleUserAuth(data: Dict):
        sid = flask.request.sid # type: ignore

        user = flask.g.user
        userId = str(user["_id"])

        flask.session["userId"] = userId
        SocketState.sidToUserId[sid] = userId
        SocketState.userIdToSid[userId] = sid

        flask_socketio.join_room(f"user_{ userId }", sid=sid) # type: ignore
        SocketQueueHandler.queueEmit("auth_success", {
            "message": "认证成功, 连接已建立"
        }, sid=sid)
        logging.info(f"用户{ userId }(SID: { sid })已认证成功并加入房间{ f'user_{ userId }' }")

    # 处理用户发送的消息
    @staticmethod
    @SocketState.socketio.on("user_message")
    @AuthenticateHelper.userAuthenticated
    def handleUserMessage(data: Dict):
        sid = flask.request.sid # type: ignore

        user = flask.g.user
        userId = str(user["_id"])
        username = user.get("name") if (user) else "未知用户"

        chatId = data.get("chatId")
        content = data.get("content")

        if (not chatId or not content):
            SocketQueueHandler.queueEmit("message_error", {
                "message": "缺少对话ID或内容"
            }, sid=sid)
            return None

        # 处理用户消息
        newMessage = MongoDBConfig.messageManager.createMessage(
            chatId=chatId,
            type="text",
            content=content,
            sender="user"
        )

        if (not newMessage):
            logging.error(f"❌ 创建新消息失败")
            return None

        chats = MongoDBConfig.chatManager.getChatById(chatId)

        if (not chats):
            logging.error(f"❌ 未找到对话: { chatId }")
            return None

        adminId = chats.get("adminId")

        if (not adminId):
            BroadcastHelper.unsignDangerousChats()
            SocketQueueHandler.queueEmit("dangerous_chats_list", {
                "chats": chats
            }, room="admin_room")

        adminSid = SocketState.adminIdToSid.get(adminId)
        chatType = chats.get("type", "normal")

        if (chatType == "dangerous" and adminSid):
            BroadcastHelper.signedDangerousChats()
            SocketQueueHandler.queueEmit("new_message", {
                "chatId": chatId,
                "userId": userId,
                "role": "user",
                "username": username,
                "content": content,
                "time": str(newMessage.get("createdAt", ""))
            }, sid=adminSid)