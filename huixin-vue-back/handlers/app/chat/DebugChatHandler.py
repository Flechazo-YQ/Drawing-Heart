import flask, logging

from states.GlobalState import GlobalState
from handlers.token.UserTokenHandler import UserTokenHandler

from mongodb_config import chat_manager

class DebugChatHandler:
        
    #调试API: 检查用户的聊天状态
    @staticmethod
    @GlobalState.app.route('/api/debug/chat-status', methods=['GET'])
    def debugChatStatus():
        token = flask.request.headers.get('Authorization')

        if not token:
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if not userId:
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            userIdString = str(userId[0])

            # 获取用户的当前聊天ID
            current_chat = GlobalState.userCurrentChats.get(userIdString, "无")

            # 获取用户的上下文长度
            context_length = len(GlobalState.userContexts.get(userIdString, []))

            # 获取用户的聊天列表
            user_chats = chat_manager.get_user_chats(userId[0])

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'user_id': userIdString,
                    'current_chat_id': current_chat,
                    'context_length': context_length,
                    'total_chats': len(user_chats),
                    'chat_list': [
                        { 
                            'id': str(chat['_id']), 
                            'title': chat['title'] 
                        } for chat in user_chats[:5]
                    ]  # 只显示前5个
                }
            })
        
        except Exception as e:
            logging.error(f"获取聊天状态失败: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取聊天状态失败: { str(e) }'
            }), 500