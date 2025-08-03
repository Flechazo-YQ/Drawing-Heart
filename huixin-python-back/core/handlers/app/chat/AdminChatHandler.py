import flask

from core.states.GlobalState import GlobalState
from core.handlers.token.AdminTokenHandler import AdminTokenHandler

class AdminChatHandler:

    # 管理员回复接口
    @staticmethod
    @GlobalState.APP.route('/api/admin/reply', methods=['POST'])
    def adminReply():
        # 验证管理员权限
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        adminUsername = AdminTokenHandler.verifyAdminToken(token)

        if (not adminUsername):
            return flask.jsonify({'message': 'Invalid admin token!'}), 401
        
        # 获取请求数据
        data = flask.request.get_json()
        userId = data.get('userId')
        adminMessage = data.get('message')

        if (not userId or not adminMessage):
            return flask.jsonify({'message': 'Missing required fields!'}), 400

        # 检查用户是否在危险对话列表中
        if (userId not in GlobalState.dangerousChats):
            return flask.jsonify({'message': 'User not found in dangerous chats!'}), 404

        # 添加管理员回复到对话记录
        GlobalState.dangerousChats[userId]['messages'].append({
            "role": "admin",
            "content": adminMessage
        })
        
        # 返回成功响应
        return flask.jsonify({
            'code': 0,
            'message': '回复成功'
        }), 200
    
    # 获取危险对话列表
    @staticmethod
    @GlobalState.APP.route('/api/admin/dangerous-chats', methods=['GET'])
    def getDangerousChats():
        # 验证管理员权限
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        adminUsername = AdminTokenHandler.verifyAdminToken(token)

        if (not adminUsername):
            return flask.jsonify({'message': 'Invalid admin token!'}), 401

        # 准备返回数据
        chatList = []

        for userId, chatData in GlobalState.dangerousChats.items():

            # 只获取最近一条消息作为预览
            lastMessage = ""
            
            if (chatData['messages']):
                lastMessage = chatData['messages'][-1]['content']

            chatList.append({
                'userId': userId,
                'username': chatData['username'],
                'lastMessage': lastMessage[:50] + "..." if (len(lastMessage) > 50) else lastMessage,
                'isActive': chatData['is_active']
            })

        return flask.jsonify({
            'code': 0,
            'chats': chatList
        }), 200
    
    # 获取特定用户的对话历史
    @staticmethod
    @GlobalState.APP.route('/api/admin/chat-history/<user_id>', methods=['GET'])
    def getChatHistory(userId):
        # 验证管理员权限
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        adminUsername = AdminTokenHandler.verifyAdminToken(token)

        if (not adminUsername):
            return flask.jsonify({'message': 'Invalid admin token!'}), 401

        # 检查用户是否在危险对话列表中
        if (userId not in GlobalState.dangerousChats):
            return flask.jsonify({'message': 'User not found in dangerous chats!'}), 404

        # 返回对话历史
        return flask.jsonify({
            'code': 0,
            'messages': GlobalState.dangerousChats[userId]['messages']
        }), 200