import flask, datetime, flask_socketio, logging

from states.SocketState import SocketState
from states.GlobalState import GlobalState
from handlers.token.UserTokenHandler import UserTokenHandler

from mongodb_config import message_manager, chat_manager

class UserSocketHandler:

    @staticmethod
    @SocketState.socketio.on('user_connect')
    def handleUserConnect(data):
        token = data.get('token')

        if (not token):
            SocketState.socketio.emit('error', {'message': 'Token is missing'})
            return

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            SocketState.socketio.emit('error', {'message': 'Invalid token'})
            return
        
        # 保存用户的连接信息
        userIdString = str(userId[0])
        GlobalState.userConnections[userIdString] = {
            'sid': flask.request.sid,
            'username': userId[1],
            'connected_at': datetime.datetime.now().isoformat()
        }
        
        # 将用户加入以用户ID命名的房间
        flask_socketio.join_room(f'user_{ userIdString }')

        # 发送连接成功响应
        SocketState.socketio.emit('connect_response', { 'status': 'success', 'message': 'Connection successful' })

        # 检查是否有未处理的消息需要发送给用户
        if (userIdString in GlobalState.dangerousChats):

            # 获取最近的管理员回复，排除系统自动生成的提示消息
            adminMessages = [
                msg for msg in GlobalState.dangerousChats[userIdString]['messages']
                if msg.get('role') == 'admin' and (

                    # 如果有messageId且不是系统风险提示，或者没有is_system标记，则包含
                    (msg.get('messageId') != 'system_risk_alert') or 
                    not msg.get('is_system', False)
                )
            ]
            
            if (adminMessages):

                # 发送最近的几条管理员消息
                recentMessages = adminMessages[-3:] if len(adminMessages) > 3 else adminMessages

                for msg in recentMessages:
                    SocketState.socketio.emit('admin_reply', {
                        'role': 'admin',
                        'content': msg.get('content'),
                        'time': msg.get('time', datetime.datetime.now().isoformat()),
                        'messageId': msg.get('messageId')  # 添加消息ID
                    }, room = f'user_{ userIdString }')

        print(f'User { userId[1] } connected with SID: { flask.request.sid }')

    @staticmethod
    @SocketState.socketio.on('user_message')
    def handleUserMessage(data):

        # 获取用户ID
        sid = flask.request.sid
        userIdString = None

        # 查找用户ID
        for uid, connectionData in GlobalState.userConnections.items():
            if (connectionData.get('sid') == sid):
                userIdString = uid
                break

        if (not userIdString):
            SocketState.socketio.emit('error', {'message': 'User not identified'})
            return
        
        content = data.get('content')

        if (not content):
            SocketState.socketio.emit('error', {'message': 'No message content'})
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
                chat_id = GlobalState.dangerousChats[userIdString].get('chat_id')
                if chat_id:
                    message_manager.add_message(
                        chat_id=chat_id,
                        message_type="text",
                        content=content,
                        sender="user"
                    )
            except Exception as e:
                logging.error(f"保存用户危险对话消息失败: {str(e)}")
            
            # 查找处理该用户的管理员
            adminId = GlobalState.dangerousChats[userIdString].get('admin_id')

            # 如果有管理员在处理，发送消息给管理员
            if (adminId and adminId in GlobalState.activeAdmins):
                SocketState.socketio.emit('new_message', {
                    'userId': userIdString,
                    'role': 'user',
                    'content': content,
                    'time': currentTime
                }, room = 'admin_room')
            else:
                # 没有管理员处理，向所有管理员发送提醒
                SocketState.socketio.emit('dangerous_chat_alert', {
                    'user': {
                        'userId': userIdString,
                        'username': GlobalState.userConnections[userIdString]['username'],
                        'lastMessage': content
                    }
                }, room = 'admin_room')
        else:
            # 创建新的危险对话记录
            # 获取用户当前的chat_id，如果没有则创建新的chat - 统一使用字符串类型
            currentChatId = GlobalState.userCurrentChats.get(userIdString)

            if (not currentChatId):

                # 为用户创建新的危险对话
                currentChatId = chat_manager.create_chat(userIdString, "危险对话", "dangerous")
                GlobalState.userCurrentChats[userIdString] = currentChatId
            else:

                # 更新现有对话为危险类型
                chat_manager.update_chat(currentChatId, {"type": "dangerous"})

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
                message_manager.add_message(
                    chat_id = currentChatId,
                    message_type = "text",
                    content = content,
                    sender = "user"
                )
            except Exception as e:
                logging.error(f"保存WebSocket用户危险消息失败: { str(e) }")
            
            # 通知所有管理员有新的危险对话
            SocketState.socketio.emit('dangerous_chat_alert', {
                'user': {
                    'userId': userIdString,
                    'username': GlobalState.userConnections[userIdString]['username'],
                    'lastMessage': content
                }
            }, room = 'admin_room')