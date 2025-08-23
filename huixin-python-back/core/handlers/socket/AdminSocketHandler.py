import flask, logging, flask_socketio

from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.states.SocketState import SocketState
from core.utils.AuthenticateHelper import AuthenticateHelper
from core.utils.BroadcastHelper import BroadcastHelper
from core.utils.type.socket.data.RequestHistoryResponseData import RequestHistoryResponseData
from core.utils.type.socket.data.AdminMessageResponseData import AdminMessageResponseData
from core.utils.type.socket.data.AdminReplyData import AdminReplyData
from core.utils.type.socket.data.NewMessageData import NewMessageData
from core.utils.token.AdminTokenHelper import AdminTokenHelper

from typing import Dict

class AdminSocketHandler:

    # 处理管理员认证
    @staticmethod
    @SocketState.socketio.on(SocketState.ADMIN_AUTH)
    @AdminTokenHelper.adminTokenRequired
    def handleAdminAuth(data: Dict):
        sid = flask.request.sid # type: ignore
        admin = flask.g.admin
        adminId = str(admin['_id'])

        AdminSocketHandler.__sessionStore(adminId)
        AdminSocketHandler.__sidAndAdminIdStore(adminId, sid)

        flask_socketio.join_room('admin_room', sid=sid) # type: ignore

        # 广播危险对话列表
        BroadcastHelper.signedDangerousChats()
        BroadcastHelper.unsignDangerousChats()

        logging.info(f'🔒 管理员登录: { adminId }')

    # 管理员请求某个对话的全部历史记录
    @staticmethod
    @SocketState.socketio.on(SocketState.ADMIN_REQUEST_HISTORY)
    @AuthenticateHelper.adminAuthenticated
    def handleRequestHistory(data: Dict):
        admin = flask.g.admin
        sid = flask.request.sid # type: ignore
        chatId = data.get('chatId')

        if (not chatId): return

        try:
            messages = MongoDBConfig.messageManager.getMessagesList(chatId)
            requestHistoryResponseData: RequestHistoryResponseData = {
                'chatId': chatId,
                'messages': messages
            }
            
            MongoDBConfig.chatManager.updater.admin(chatId, str(admin['_id']))
            SocketQueueHandler.queueEmit(
                SocketState.REQUEST_HISTORY_RESPONSE['event'],
                requestHistoryResponseData,
                sid=sid
            )

            # 广播危险对话列表
            BroadcastHelper.signedDangerousChats()
            BroadcastHelper.unsignDangerousChats()
        except Exception as e:
            logging.error(f'❌ 获取对话{ chatId }历史失败: { str(e) }')

    # 处理管理员发送的消息
    @staticmethod
    @SocketState.socketio.on(SocketState.ADMIN_MESSAGE)
    @AuthenticateHelper.adminAuthenticated
    def handleAdminMessage(data: Dict):
        sid = flask.request.sid # type: ignore

        admin = flask.g.admin
        adminId = str(admin['_id'])

        chatId = data.get('chatId')
        content = data.get('content')

        if (not chatId or not content):
            adminMessageResponseData: AdminMessageResponseData = {
                'status': 'error',
                'message': '缺少对话ID或内容'
            }
            SocketQueueHandler.queueEmit(
                SocketState.ADMIN_MESSAGE_RESPONSE['event'],
                adminMessageResponseData,
                sid=sid
            )
            return
        
        chat = MongoDBConfig.chatManager.getChatById(chatId)

        newMessage = MongoDBConfig.messageManager.createMessage(
            chatId=chatId,
            type='text',
            content=content,
            sender='admin'
        )

        logging.info(newMessage.get('timestamp', '')) if (newMessage) else logging.error('创建新消息失败')

        if (not newMessage):
            raise Exception('创建新消息失败')
        
        adminMessageResponseData: AdminMessageResponseData = {
            'status': 'success',
            'message': '消息发送成功'
        }

        SocketQueueHandler.queueEmit(
            SocketState.ADMIN_MESSAGE_RESPONSE['event'], 
            adminMessageResponseData, 
            sid=sid
        )

        if (not chat):
            adminMessageResponseData: AdminMessageResponseData = {
                'status': 'error',
                'message': '未找到对话'
            }
            
            SocketQueueHandler.queueEmit(
                SocketState.ADMIN_MESSAGE_RESPONSE['event'], 
                adminMessageResponseData, 
                sid=sid
            )
            return

        adminReplyData: AdminReplyData = {
            'chatId': chatId,
            'content': content,
            'timestamp': str(newMessage.get('timestamp', ''))
        }

        SocketQueueHandler.queueEmit(
            SocketState.ADMIN_REPLY['event'], 
            adminReplyData, 
            room='user_' + chat['userId']
        )

        MongoDBConfig.chatManager.updater.admin(chatId, adminId)

        # 发送新消息定义
        newMessageData: NewMessageData = {
            'userId': chat['userId'],
            'chatId': chatId,
            'role': 'admin',
            'content': content,
            'timestamp': str(newMessage.get('timestamp', ''))
        }

        # 发送给用户
        SocketQueueHandler.queueEmit(
            SocketState.NEW_MESSAGE['event'], 
            newMessageData, 
            room='user_' + chat['userId']
        )

        # 发送给管理员
        SocketQueueHandler.queueEmit(
            SocketState.NEW_MESSAGE['event'], 
            newMessageData, 
            sid=sid
        )

        if (chat and 'userId' in chat):
            adminMessageResponseData: AdminMessageResponseData = {
                'status': 'success',
                'message': '消息发送成功'
            }
            
            SocketQueueHandler.queueEmit(
                SocketState.ADMIN_MESSAGE_RESPONSE['event'],
                adminMessageResponseData,
                room='user_' + chat['userId']
            )

    # 存储管理员id到session
    @staticmethod
    def __sessionStore(adminId: str):
        flask.session['adminId'] = adminId

    # 存储管理员sid及id间的映射
    @staticmethod
    def __sidAndAdminIdStore(adminId: str, sid: str):
        SocketState.adminIdToSid[adminId] = sid
        SocketState.sidToAdminId[sid] = adminId
