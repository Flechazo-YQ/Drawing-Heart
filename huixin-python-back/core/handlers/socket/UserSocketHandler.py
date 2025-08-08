import flask, datetime, flask_socketio, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler

class UserSocketHandler:

    @staticmethod
    @SocketState.socketio.on('user_connect')
    def handleUserConnect(data: dict):
        token = data.get('token')
        sid = flask.request.sid # type: ignore

        if (not token):
            SocketQueueHandler.queueEmit('error', {
                'message': 'Token is missing'
            })
            return

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            SocketQueueHandler.queueEmit('error', {
                'message': 'Invalid token'
            })
            return

        user = MongoDBConfig.userManager.getUserById(userId)

        if (not user):
            SocketQueueHandler.queueEmit('error', {
                'message': 'User not found'
            })
            return

        username = user.get('username', '未知用户')

        GlobalState.userConnections[userId] = {
            'sid': sid,
            'username': username,
            'connected_at': datetime.datetime.now().isoformat()
        }
        GlobalState.sidToUserId[sid] = userId

        flask_socketio.join_room(f'user_{ userId }')
        SocketQueueHandler.queueEmit('connect_response', {
            'status': 'success', 
            'message': 'Connection successful'
        })

        if (userId in GlobalState.dangerousChats):
            adminMessages = [
                msg for msg in GlobalState.dangerousChats[userId]['messages']
                if (
                    msg.get('role') == 'admin' 
                    and ((msg.get('messageId') != 'system_risk_alert') or not msg.get('is_system', False))
                )
            ]
            if (adminMessages):
                recentMessages = adminMessages[-3:] if (len(adminMessages) > 3) else adminMessages

                for msg in recentMessages:
                    SocketQueueHandler.queueEmit('admin_reply', {
                        'role': 'admin',
                        'content': msg.get('content'),
                        'time': msg.get('time', datetime.datetime.now().isoformat()),
                        'messageId': msg.get('messageId')
                    }, f'user_{ userId }') # type: ignore

        logging.info(f'User { username } connected with SID: { request.sid }') # type: ignore

    @staticmethod
    @SocketState.socketio.on('user_message')
    def handleUserMessage(data: dict):
        sid = flask.request.sid # type: ignore
        userId = GlobalState.sidToUserId.get(sid)

        if (not userId):
            SocketQueueHandler.queueEmit('error', {
                'message': 'User not identified'
            })
            return
        
        content = data.get('content')

        if (not content):
            SocketQueueHandler.queueEmit('error', {
                'message': 'No message content'
            })
            return
        
        currentTime = datetime.datetime.now().isoformat()
        
        # 添加消息到危险对话记录
        if (userId in GlobalState.dangerousChats):
            GlobalState.dangerousChats[userId]['messages'].append({
                'role': 'user',
                'content': content,
                'time': currentTime
            })
            
            # 保存用户消息到数据库
            try:
                chatId = GlobalState.dangerousChats[userId].get('chat_id')

                if (chatId):
                    MongoDBConfig.messageManager.addMessage(
                        chatId=chatId,
                        messageType="text",
                        content=content,
                        sender="user"
                    )
            except Exception as e:
                logging.error(f"保存用户危险对话消息失败: { str(e) }")
            
            # 查找处理该用户的管理员
            adminId = GlobalState.dangerousChats[userId].get('admin_id')

            # 如果有管理员在处理，发送消息给管理员
            if (adminId and adminId in GlobalState.activeAdmins):
                SocketQueueHandler.queueEmit('new_message', {
                    'userId': userId,
                    'role': 'user',
                    'content': content,
                    'time': currentTime
                }, 'admin_room') # type: ignore
            else:
                # 没有管理员处理，向所有管理员发送提醒
                SocketQueueHandler.queueEmit('dangerous_chat_alert', {
                    'user': {
                        'userId': userId,
                        'username': GlobalState.userConnections[userId]['username'],
                        'lastMessage': content
                    }
                }, 'admin_room') # type: ignore
        else:
            # 创建新的危险对话记录
            # 获取用户当前的chat_id，如果没有则创建新的chat - 统一使用字符串类型
            currentChatId = GlobalState.userCurrentChats.get(userId)

            if (not currentChatId):

                # 为用户创建新的危险对话
                currentChatId = MongoDBConfig.chatManager.createChat(userId, "危险对话", "dangerous")
                GlobalState.userCurrentChats[userId] = currentChatId
            else:

                # 更新现有对话为危险类型
                MongoDBConfig.chatManager.updateChat(currentChatId, {"type": "dangerous"})

            GlobalState.dangerousChats[userId] = {
                'username': GlobalState.userConnections[userId]['username'],
                'chat_id': currentChatId,  # 添加chat_id
                'messages': [{
                    'role': 'user',
                    'content': content,
                    'time': currentTime
                }],
                'is_active': True,
                'admin_id': None
            }
            
            # 保存用户消息到数据库
            try:
                MongoDBConfig.messageManager.addMessage(
                    chatId=currentChatId,
                    messageType="text",
                    content=content,
                    sender="user"
                )
            except Exception as e:
                logging.error(f"保存WebSocket用户危险消息失败: { str(e) }")
            
            # 通知所有管理员有新的危险对话
            SocketQueueHandler.queueEmit('dangerous_chat_alert', {
                'user': {
                    'userId': userId,
                    'username': GlobalState.userConnections[userId]['username'],
                    'lastMessage': content
                }
            }, 'admin_room') # type: ignore