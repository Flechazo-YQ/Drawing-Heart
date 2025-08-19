import flask, logging, flask_socketio

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.handlers.token.AdminTokenHandler import AdminTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.utils.AuthenticateHelper import AuthenticateHelper
from core.utils.FormatHelper import FormatHelper

from typing import Dict

class AdminSocketHandler:

    # 广播危险需要干预的对话
    @staticmethod
    def __broadcastInterventionList():
        try:
            chats = MongoDBConfig.chatManager.getUnsignedDangerousChats()
            formattedChats = FormatHelper.json(chats)

            for (chat) in formattedChats:
                userId = chat.get("userId")
                user = MongoDBConfig.userManager.getUserById(userId)
                username = user.get("name") if (user is not None) else "未知用户"
                chat["username"] = username

            SocketQueueHandler.queueEmit("dangerous_chats_list", {
                "chats": formattedChats
            }, room="admin_room")
        except Exception as e:
            logging.error(f"❌ 获取未签名危险对话失败: {str(e)}")

    # 处理管理员认证
    @staticmethod
    @SocketState.socketio.on("admin_auth")
    @AdminTokenHandler.adminTokenRequired
    def handleAdminAuth(data: Dict):
        admin = flask.g.admin
        sid = flask.request.sid # type: ignore
        adminId = str(admin["_id"])
        flask.session["adminId"] = adminId
        SocketState.sidToAdminId[sid] = adminId
        SocketState.adminIdToSid[adminId] = sid

        flask_socketio.join_room("admin_room", sid=sid) # type: ignore
        AdminSocketHandler.__broadcastInterventionList()
        logging.info(f"🔒 管理员登录: { adminId }")

    # 管理员请求某个对话的全部历史记录
    @staticmethod
    @SocketState.socketio.on("request_history")
    @AuthenticateHelper.adminAuthenticated
    def handleRequestHistory(data: Dict):
        admin = flask.g.admin
        sid = flask.request.sid # type: ignore
        chatId = data.get("chatId")

        if (not chatId): return

        try:
            messages = MongoDBConfig.messageManager.getAllMessages(chatId)
            chatInfo = MongoDBConfig.chatManager.getChatById(chatId)
            response = {
                "chatId": chatId,
                "messages": messages,
                "chatInfo": chatInfo
            }

            MongoDBConfig.chatManager.updater.admin(chatId, str(admin["_id"]))
            SocketQueueHandler.queueEmit("request_history_response", response, sid=sid) # type: ignore
            AdminSocketHandler.__broadcastInterventionList()
        except Exception as e:
            logging.error(f"❌ 获取对话{ chatId }历史失败: { str(e) }")

    # 处理管理员发送的消息
    @staticmethod
    @SocketState.socketio.on("admin_message")
    @AuthenticateHelper.adminAuthenticated
    def handleAdminMessage(data: Dict):
        admin = flask.g.admin
        adminName = admin["name"]
        sid = flask.request.sid # type: ignore
        chatId = data.get("chatId")
        content = data.get("content")

        if (not chatId or not content):
            SocketQueueHandler.queueEmit("admin_message_response", {
                "status": "error",
                "message": "Chat ID and content are required"
            }, sid=sid) # type: ignore
            return

        try:
            newMessage = MongoDBConfig.messageManager.createMessage(
                chatId=chatId,
                type="text",
                content=content,
                sender="admin"
            )

            if (not newMessage):
                raise Exception("Failed to create message")

            SocketQueueHandler.queueEmit("admin_message_response", {
                "status": "success",
                "message": "Message sent successfully"
            }, sid=sid) # type: ignore

            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (not chat):
                SocketQueueHandler.queueEmit("admin_message_response", {
                    "status": "error",
                    "message": "Chat not found"
                }, sid=sid) # type: ignore
                return

            SocketQueueHandler.queueEmit("new_message", {
                "userId": chat["userId"],
                "role": "admin",
                "content": content,
                "time": str(newMessage.get("createdAt", ""))
            }, room="user_" + chat["userId"])

            if (chat and "userId" in chat):
                SocketQueueHandler.queueEmit("admin_message_response", {
                    "status": "success",
                    "message": "Message sent successfully"
                }, room="user_" + chat["userId"]) # type: ignore
        except Exception as e:
            logging.error(f"❌ 发送管理员{ adminName }消息到对话{ chatId }失败: { str(e) }")
