import flask, logging, flask_socketio

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.handlers.token.AdminTokenHandler import AdminTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.utils.AuthenticateHelper import AuthenticateHelper
from core.utils.BroadcastHelper import BroadcastHelper

from typing import Dict

class AdminSocketHandler:

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

        # 广播危险对话列表
        BroadcastHelper.signedDangerousChats()
        BroadcastHelper.unsignDangerousChats()

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
            messages = MongoDBConfig.messageManager.getMessagesList(chatId)
            
            MongoDBConfig.chatManager.updater.admin(chatId, str(admin["_id"]))
            SocketQueueHandler.queueEmit("request_history_response", {
                "chatId": chatId,
                "messages": messages
            }, sid=sid)

            # 广播危险对话列表
            BroadcastHelper.signedDangerousChats()
            BroadcastHelper.unsignDangerousChats()
        except Exception as e:
            logging.error(f"❌ 获取对话{ chatId }历史失败: { str(e) }")

    # 处理管理员发送的消息
    @staticmethod
    @SocketState.socketio.on("admin_message")
    @AuthenticateHelper.adminAuthenticated
    def handleAdminMessage(data: Dict):
        sid = flask.request.sid # type: ignore

        admin = flask.g.admin
        adminId = str(admin["_id"])

        chatId = data.get("chatId")
        content = data.get("content")

        if (not chatId or not content):
            SocketQueueHandler.queueEmit("admin_message_response", {
                "status": "error",
                "message": "缺少对话ID或内容"
            }, sid=sid) # type: ignore
            return
        
        chat = MongoDBConfig.chatManager.getChatById(chatId)

        newMessage = MongoDBConfig.messageManager.createMessage(
            chatId=chatId,
            type="text",
            content=content,
            sender="admin"
        )

        logging.info(newMessage.get("timestamp", "")) if (newMessage) else logging.error("创建新消息失败")

        if (not newMessage):
            raise Exception("创建新消息失败")

        SocketQueueHandler.queueEmit("admin_message_response", {
            "status": "success",
            "message": "消息发送成功"
        }, sid=sid) # type: ignore

        if (not chat):
            SocketQueueHandler.queueEmit("admin_message_response", {
                "status": "error",
                "message": "未找到对话"
            }, sid=sid) # type: ignore
            return
        
        SocketQueueHandler.queueEmit("admin_reply", {
            "chatId": chatId,
            "content": content,
            "timestamp": str(newMessage.get("timestamp", ""))
        }, room="user_" + chat["userId"])

        MongoDBConfig.chatManager.updater.admin(chatId, adminId)

        # 发送给用户
        SocketQueueHandler.queueEmit("new_message", {
            "userId": chat["userId"],
            "chatId": chatId,
            "role": "admin",
            "content": content,
            "timestamp": str(newMessage.get("timestamp", ""))
        }, room="user_" + chat["userId"])

        # 发送给管理员
        SocketQueueHandler.queueEmit("new_message", {
            "userId": chat["userId"],
            "chatId": chatId,
            "role": "admin",
            "content": content,
            "timestamp": str(newMessage.get("timestamp", ""))
        }, sid=sid)

        if (chat and "userId" in chat):
            SocketQueueHandler.queueEmit("admin_message_response", {
                "status": "success",
                "message": "消息发送成功"
            }, room="user_" + chat["userId"])
