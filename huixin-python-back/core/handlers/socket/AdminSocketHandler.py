import flask, datetime, flask_socketio, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState
from core.handlers.token.AdminTokenHandler import AdminTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler

class AdminSocketHandler:

    @staticmethod
    @SocketState.socketio.on('admin_auth')
    def handleAdminAuth(data: dict):
        token = data.get('token')
        sid = flask.request.sid # type: ignore

        if (not token):
            SocketQueueHandler.queueEmit('auth_response', {
                'status': 'error', 
                'message': 'Token is missing'
            }, sid=sid)
            return

        adminId = AdminTokenHandler.verifyAdminToken(token)

        if (not adminId):
            SocketQueueHandler.queueEmit('auth_response', {
                'status': 'error', 
                'message': 'Invalid token'
            }, sid=sid)
            return
        
        # 保存管理员的会话ID
        GlobalState.activeAdmins[adminId] = {
            'sid': sid,
            'connected_at': datetime.datetime.now().isoformat()
        }
        GlobalState.sidToAdminId[sid] = adminId

        # 将管理员加入管理员房间
        flask_socketio.join_room('admin_room')

        # 发送认证成功响应
        SocketQueueHandler.queueEmit('auth_response', {
            'status': 'success',
            'message': 'Authentication successful'
        }, 'admin_room', sid)

        # 发送当前所有危险对话列表
        chatList = []

        for userId, chatData in GlobalState.dangerousChats.items():

            # 只获取最近一条消息作为预览
            lastMessage = ''

            if (chatData['messages']):
                lastMessage = chatData['messages'][-1]['content']

            chatList.append({
                'userId': userId,
                'username': chatData['username'],
                'lastMessage': lastMessage[:50] + "..." if (len(lastMessage) > 50) else lastMessage,
                'isActive': chatData['is_active']
            })

        SocketQueueHandler.queueEmit('dangerous_chats_list', { 
            'chats': chatList 
        }, 'admin_room', sid)

    @staticmethod
    @SocketState.socketio.on('request_history')
    def handleRequestHistory(data: dict):

        # 验证是否为管理员
        sid = flask.request.sid # type: ignore
        adminId = GlobalState.sidToAdminId.get(sid)

        if (not adminId):
            SocketQueueHandler.queueEmit('error', {
                'message': 'Unauthorized'
            }, sid=sid)
            return
        
        userId = data.get('userId')

        if (not userId or userId not in GlobalState.dangerousChats):
            SocketQueueHandler.queueEmit('error', {
                'message': 'User not found'
            }, sid=sid)
            return
        
        # 发送历史记录
        SocketQueueHandler.queueEmit('chat_history', {
            'userId': userId,
            'username': GlobalState.dangerousChats[userId]['username'],
            'messages': GlobalState.dangerousChats[userId]['messages']
        }, sid=sid)

        # 设置该管理员为当前处理该用户的管理员
        GlobalState.dangerousChats[userId]['admin_id'] = adminId

    @staticmethod
    @SocketState.socketio.on('admin_message')
    def handleAdminMessage(data: dict):

        # 验证是否为管理员
        sid = flask.request.sid # type: ignore
        adminId = GlobalState.sidToAdminId.get(sid)

        if (not adminId):
            SocketQueueHandler.queueEmit('error', {
                'message': 'Unauthorized'
            }, sid=sid)
            return

        userId = data.get('userId')
        content = data.get('content')
        messageId = data.get('messageId')  # 获取消息ID

        if (not userId or not content or userId not in GlobalState.dangerousChats):
            SocketQueueHandler.queueEmit('error', {
                'message': 'Invalid request'
            }, sid=sid)
            return
        
        currentTime = datetime.datetime.now().isoformat()
        
        # 添加消息到危险对话记录
        GlobalState.dangerousChats[userId]['messages'].append({
            'role': 'admin',
            'content': content,
            'time': currentTime,
            'messageId': messageId  # 存储消息ID
        })
        
        # 保存管理员消息到数据库
        try:
            chatId = GlobalState.dangerousChats[userId].get('chat_id')

            if (chatId):
                MongoDBConfig.messageManager.addMessage(
                    chatId = chatId,
                    messageType = "text",
                    content = content,
                    sender = "admin"
                )
        except Exception as e:
            logging.error(f"保存管理员消息失败: { str(e) }")
        
        # 发送消息给所有管理员，更新聊天状态
        SocketQueueHandler.queueEmit('new_message', {
            'userId': userId,
            'role': 'admin',
            'content': content,
            'sender': adminId,
            'time': currentTime,
            'messageId': messageId  # 添加消息ID
        }, 'admin_room', sid) # type: ignore
        
        # 向用户发送消息 - 检查用户是否有活跃的会话
        if (userId in GlobalState.userConnections):

            # 向用户的房间发送消息
            SocketQueueHandler.queueEmit('admin_reply', {
                'role': 'admin',
                'content': content,
                'time': currentTime,
                'messageId': messageId  # 添加消息ID
            }, f'user_{ userId }', sid) # type: ignore
        else:
            # 如果用户不在线，将消息标记为未读，等用户重连时发送
                print(f"User { userId } is not connected, message will be delivered when they reconnect")