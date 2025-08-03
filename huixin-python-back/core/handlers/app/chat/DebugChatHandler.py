import flask, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.app.chat.UserChatHandler import UserChatHandler

class DebugChatHandler:
        
    #调试API: 检查用户的聊天状态
    @staticmethod
    @GlobalState.APP.route('/api/debug/chat-status', methods=['GET'])
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
            currentChat = GlobalState.userCurrentChats.get(userIdString, "无")

            # 获取用户的上下文长度
            contextLength = len(GlobalState.userContexts.get(userIdString, []))

            # 获取用户的聊天列表
            userChats = MongoDBConfig.chatManager.getUserChats(userId[0])

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'user_id': userIdString,
                    'current_chat_id': currentChat,
                    'context_length': contextLength,
                    'total_chats': len(userChats),
                    'chat_list': [
                        { 
                            'id': str(chat['_id']), 
                            'title': chat['title'] 
                        } for chat in userChats[:5]
                    ]  # 只显示前5个
                }
            })
        
        except Exception as e:
            logging.error(f"获取聊天状态失败: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取聊天状态失败: { str(e) }'
            }), 500
        
    # 调试API: 检查危险检测功能
    @staticmethod
    @GlobalState.APP.route('/api/test-danger-detection', methods=['POST'])
    def testDangerDetection():
        try:
            data = flask.request.get_json()
            testMessage = data.get('message', '')

            if (not testMessage):
                return flask.jsonify({'error': '消息不能为空'}), 400

            # 直接调用危险检测函数
            dangerScore = UserChatHandler.processMessage(testMessage)

            return flask.jsonify({
                'message': testMessage,
                'danger_score': float(dangerScore),
                'is_dangerous': dangerScore > 0.3,
                'threshold': 0.3
            })
        except Exception as e:
            return flask.jsonify({'error': str(e)}), 500
