import flask, datetime, flask_socketio, logging

from states.SocketState import SocketState
from states.GlobalState import GlobalState
from handlers.token.AdminTokenHandler import AdminTokenHandler

from mongodb_config import message_manager

class AdminSocketHandler:

    @staticmethod
    @SocketState.socketio.on('admin_auth')
    def handleAdminAuth(data):
        token = data.get('token')

        if (not token):
            SocketState.socketio.emit('auth_response', {'status': 'error', 'message': 'Token is missing'})
            return

        adminUsername = AdminTokenHandler.verifyAdminToken(token)
        if not adminUsername:
            SocketState.socketio.emit('auth_response', {'status': 'error', 'message': 'Invalid token'})
            return
        
        # 保存管理员的会话ID
        sid = flask.request.sid
        GlobalState.activeAdmins[adminUsername] = {
            'sid': sid,
            'connected_at': datetime.datetime.now().isoformat()
        }
        
        # 将管理员加入管理员房间
        flask_socketio.join_room('admin_room')

        # 发送认证成功响应
        SocketState.socketio.emit('auth_response', {'status': 'success', 'message': 'Authentication successful'})

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
                'lastMessage': lastMessage[:50] + "..." if len(lastMessage) > 50 else lastMessage,
                'isActive': chatData['is_active']
            })

        SocketState.socketio.emit('dangerous_chats_list', { 'chats': chatList })

    @staticmethod
    @SocketState.socketio.on('request_history')
    def handleRequestHistory(data):

        # 验证是否为管理员
        sid = flask.request.sid
        adminUsername = None

        for username, admin_data in GlobalState.activeAdmins.items():
            if (admin_data.get('sid') == sid):
                adminUsername = username
                break

        if (not adminUsername):
            SocketState.socketio.emit('error', {'message': 'Unauthorized'})
            return
        
        userId = data.get('userId')

        if (not userId or userId not in GlobalState.dangerousChats):
            SocketState.socketio.emit('error', {'message': 'User not found'})
            return
        
        # 发送历史记录
        SocketState.socketio.emit('chat_history', {
            'userId': userId,
            'username': GlobalState.dangerousChats[userId]['username'],
            'messages': GlobalState.dangerousChats[userId]['messages']
        })
        
        # 设置该管理员为当前处理该用户的管理员
        GlobalState.dangerousChats[userId]['admin_id'] = adminUsername

    @staticmethod
    @SocketState.socketio.on('admin_message')
    def handleAdminMessage(data):

        # 验证是否为管理员
        sid = flask.request.sid
        adminUsername = None

        for username, admin_data in GlobalState.activeAdmins.items():
            if (admin_data.get('sid') == sid):
                adminUsername = username
                break

        if (not adminUsername):
            SocketState.socketio.emit('error', {'message': 'Unauthorized'})
            return
        
        userId = data.get('userId')
        content = data.get('content')
        messageId = data.get('messageId')  # 获取消息ID

        if (not userId or not content or userId not in GlobalState.dangerousChats):
            SocketState.socketio.emit('error', {'message': 'Invalid request'})
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
                message_manager.add_message(
                    chat_id = chatId,
                    message_type = "text",
                    content = content,
                    sender = "admin"
                )
        except Exception as e:
            logging.error(f"保存管理员消息失败: { str(e) }")
        
        # 发送消息给所有管理员，更新聊天状态
        SocketState.socketio.emit('new_message', {
            'userId': userId,
            'role': 'admin',
            'content': content,
            'sender': adminUsername,
            'time': currentTime,
            'messageId': messageId  # 添加消息ID
        }, room = 'admin_room')
        
        # 向用户发送消息 - 检查用户是否有活跃的会话
        if (userId in GlobalState.userConnections):

            # 向用户的房间发送消息
            SocketState.socketio.emit('admin_reply', {
                'role': 'admin',
                'content': content,
                'time': currentTime,
                'messageId': messageId  # 添加消息ID
            }, room = f'user_{ userId }')
        else:
            # 如果用户不在线，将消息标记为未读，等用户重连时发送
            print(f"User { userId } is not connected, message will be delivered when they reconnect")