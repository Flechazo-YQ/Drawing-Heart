import flask, datetime, flask_socketio, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler

class UserSocketHandler:

    @staticmethod
    @SocketState.SOCKETIO.on('user_connect')
    def handleUserConnect(data: dict):
        token = data.get('token')
        userId = None
        username = None

        # 优先使用前端传递的 userId 和 username
        if ('userId' in data and 'username' in data):
            userIdString = str(data['userId'])
            username = data['username']

            # 校验token有效性
            if (token):
                userIdCheck = UserTokenHandler.verifyUserToken(token)

                if (
                    not userIdCheck
                    or (isinstance(userIdCheck, (list, tuple)) and str(userIdCheck[0]) != userIdString)
                ):
                    flask_socketio.emit('error', {'message': 'Invalid token'})
                    return
        else:
            if (not token):
                flask_socketio.emit('error', {'message': 'Token is missing'})
                return
            
            userId = UserTokenHandler.verifyUserToken(token)

            if (not userId):
                flask_socketio.emit('error', {'message': 'Invalid token'})
                return
            
            if (isinstance(userId, (list, tuple))):
                userIdString = str(userId[0])
                username = userId[1] if (len(userId) > 1) else "未知用户"
            else:
                userIdString = str(userId)
                username = "未知用户"

        GlobalState.userConnections[userIdString] = {
            'sid': flask.request.sid, # type: ignore
            'username': username,
            'connected_at': datetime.datetime.now().isoformat()
        }

        flask_socketio.join_room(f'user_{ userIdString }')
        flask_socketio.emit('connect_response', {'status': 'success', 'message': 'Connection successful'})

        if (userIdString in GlobalState.dangerousChats):
            adminMessages = [
                msg for msg in GlobalState.dangerousChats[userIdString]['messages']
                if (
                    msg.get('role') == 'admin' 
                    and ((msg.get('messageId') != 'system_risk_alert') or not msg.get('is_system', False))
                )
            ]
            if (adminMessages):
                recentMessages = adminMessages[-3:] if (len(adminMessages) > 3) else adminMessages

                for msg in recentMessages:
                    SocketState.SOCKETIO.emit(
                        'admin_reply', 
                        {
                            'role': 'admin',
                            'content': msg.get('content'),
                            'time': msg.get('time', datetime.datetime.now().isoformat()),
                            'messageId': msg.get('messageId')
                        }, 
                        room=f'user_{ userIdString }' # type: ignore
                    )

        print(f'User { username } connected with SID: { request.sid }') # type: ignore

    @staticmethod
    @SocketState.SOCKETIO.on('user_message')
    def handleUserMessage(data: dict):

        # 获取用户ID
        sid = flask.request.sid # type: ignore
        userIdString = None

        # 查找用户ID
        for uid, connectionData in GlobalState.userConnections.items():
            if (connectionData.get('sid') == sid):
                userIdString = uid
                break

        if (not userIdString):
            SocketState.SOCKETIO.emit('error', {'message': 'User not identified'})
            return
        
        content = data.get('content')

        if (not content):
            SocketState.SOCKETIO.emit('error', {'message': 'No message content'})
            return
        
        currentTime = datetime.datetime.now().isoformat()
        
        # 添加消息到危险对话记录
        if (userIdString in GlobalState.dangerousChats):
            GlobalState.dangerousChats[userIdString]['messages'].append({
                'role': 'user',
                'content': content,
                'time': currentTime
            })
            
            # 保存用户消息到数据库
            try:
                chatId = GlobalState.dangerousChats[userIdString].get('chat_id')
                if chatId:
                    MongoDBConfig.messageManager.addMessage(
                        chatId=chatId,
                        messageType="text",
                        content=content,
                        sender="user"
                    )
            except Exception as e:
                logging.error(f"保存用户危险对话消息失败: { str(e) }")
            
            # 查找处理该用户的管理员
            adminId = GlobalState.dangerousChats[userIdString].get('admin_id')

            # 如果有管理员在处理，发送消息给管理员
            if (adminId and adminId in GlobalState.activeAdmins):
                SocketState.SOCKETIO.emit('new_message', {
                    'userId': userIdString,
                    'role': 'user',
                    'content': content,
                    'time': currentTime
                }, room = 'admin_room') # type: ignore
            else:
                # 没有管理员处理，向所有管理员发送提醒
                SocketState.SOCKETIO.emit('dangerous_chat_alert', {
                    'user': {
                        'userId': userIdString,
                        'username': GlobalState.userConnections[userIdString]['username'],
                        'lastMessage': content
                    }
                }, room = 'admin_room') # type: ignore
        else:
            # 创建新的危险对话记录
            # 获取用户当前的chat_id，如果没有则创建新的chat - 统一使用字符串类型
            currentChatId = GlobalState.userCurrentChats.get(userIdString)

            if (not currentChatId):

                # 为用户创建新的危险对话
                currentChatId = MongoDBConfig.chatManager.createChat(userIdString, "危险对话", "dangerous")
                GlobalState.userCurrentChats[userIdString] = currentChatId
            else:

                # 更新现有对话为危险类型
                MongoDBConfig.chatManager.updateChat(currentChatId, {"type": "dangerous"})

            GlobalState.dangerousChats[userIdString] = {
                'username': GlobalState.userConnections[userIdString]['username'],
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
            SocketState.SOCKETIO.emit('dangerous_chat_alert', {
                'user': {
                    'userId': userIdString,
                    'username': GlobalState.userConnections[userIdString]['username'],
                    'lastMessage': content
                }
            }, room = 'admin_room') # type: ignore