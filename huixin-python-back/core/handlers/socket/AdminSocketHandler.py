import flask, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.handlers.token.AdminTokenHandler import AdminTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.utils.AuthenticateHelper import AuthenticateHelper

from typing import Dict

class AdminSocketHandler:

    @classmethod
    @AdminTokenHandler.adminTokenRequired
    @SocketState.socketio.on('admin_auth')
    def handleAdminAuth(cls, admin: Dict):
        sid = flask.request.sid # type: ignore
        adminId = str(admin["_id"])
        flask.session["adminId"] = adminId

        SocketQueueHandler.queueEmit('auth_response', {
            'status': 'success',
            'message': 'Authentication successful'
        }, 'admin_room', sid) # type: ignore

        logging.info(f"管理员 { adminId } 已认证成功, socket ID: { sid }")
        cls.broadcastInterventionList()

    # 广播危险需要干预的对话
    @staticmethod
    def broadcastInterventionList():
        try:
            chats = MongoDBConfig.chatManager.getUnsignedDangerousChats()
            SocketQueueHandler.queueEmit('dangerous_chats_list', {
                'chats': chats
            }, 'admin_room')
        except Exception as e:
            logging.error(f"获取未签名危险对话失败: {str(e)}")

    # 管理员请求某个对话的全部历史记录
    @classmethod
    @AuthenticateHelper.adminAuthenticated
    @SocketState.socketio.on('request_history')
    def handleRequestHistory(cls, admin: Dict, data: Dict):
        chatId = data.get('chatId')

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
            SocketQueueHandler.queueEmit('request_history_response', response, sid=sid) # type: ignore
            cls.broadcastInterventionList()
        except Exception as e:
            logging.error(f"获取对话{ chatId }历史失败: { str(e) }")

    @staticmethod
    @AuthenticateHelper.adminAuthenticated
    @SocketState.socketio.on('admin_message')
    def handleAdminMessage(admin: Dict, data: Dict):
        chatId = data.get('chatId')
        content = data.get('content')

        if (not chatId or not content):
            SocketQueueHandler.queueEmit('admin_message_response', {
                'status': 'error',
                'message': 'Chat ID and content are required'
            }, sid=flask.request.sid) # type: ignore
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

            SocketQueueHandler.queueEmit('admin_message_response', {
                'status': 'success',
                'message': 'Message sent successfully'
            }, room="admin_room", sid=flask.request.sid) # type: ignore

            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (chat and "userId" in chat):
                SocketQueueHandler.queueEmit('admin_message_response', {
                    'status': 'success',
                    'message': 'Message sent successfully'
                }, room="user_" + chat["userId"], sid=flask.request.sid) # type: ignore
        except Exception as e:
            logging.error(f"❌ 发送管理员{ str(admin['_id']) }消息到对话{ chatId }失败: { str(e) }")
