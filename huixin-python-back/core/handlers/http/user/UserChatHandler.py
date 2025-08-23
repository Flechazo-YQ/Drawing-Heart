import logging, flask

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.http.StreamChatHandler import StreamChatHandler
from core.states.route.ApiState import ApiState
from core.utils.token.UserTokenHelper import UserTokenHelper

class UserChatHandler:

    # 创建新对话
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.NEW_CHAT['route'], methods=ApiState.NEW_CHAT['method'])
    @UserTokenHelper.userTokenRequired
    def createNewChat():
        try:
            user = flask.g.user
            data = flask.request.get_json() or {}
            title = data.get('title', '新对话')
            userId = str(user['_id'])
            chatId = MongoDBConfig.chatManager.createChat(userId, title)

            if (not chatId):
                raise Exception('无法创建对话')

            return flask.jsonify({
                'code': 0,
                'message': '创建对话成功',
                'data': {
                    'chatId': chatId,
                    'title': title
                }
            }), 201
        except Exception as e:
            logging.error(f'❌ 创建新对话失败: { str(e) }')
            return flask.jsonify({
                'code': 500,
                'message': f'创建对话失败: { str(e) }'
            }), 500

    # 隐藏对话
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.HIDE_CHAT['route'], methods=ApiState.HIDE_CHAT['method'])
    @UserTokenHelper.userTokenRequired
    def hideChat(chatId: str):
        try:
            user = flask.g.user
            userId = str(user['_id'])
            success = MongoDBConfig.chatManager.updater.hide(chatId, userId)

            if (not success):
                return flask.jsonify({
                    'code': 404,
                    'message': '隐藏对话失败'
                }), 404

            return flask.jsonify({
                'code': 0,
                'message': '隐藏对话成功'
            }), 200
        except Exception as e:
            logging.error(f'❌ 隐藏对话失败: { str(e) }')
            return flask.jsonify({
                'code': 500,
                'message': f'隐藏对话失败: { str(e) }'
            }), 500
        
    # 流式聊天接口(AI对话)
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.CHAT_STREAM['route'], methods=ApiState.CHAT_STREAM['method'])
    @UserTokenHelper.userTokenRequired
    def streamChat():
        user = flask.g.user
        data = flask.request.get_json()

        if (not data):
            return flask.jsonify({
                'code': 400,
                'message': '请求数据不能为空!'
            }), 400
        
        
        userMessage = data.get('message', '')
        userId = str(user['_id'])
        chatId = data.get('chatId')

        if (isinstance(chatId, dict)):
            chatId = chatId.get('id')

        try:
            if (not chatId):
                chat = MongoDBConfig.chatManager.createChat(userId, '新对话')

                if (not chat):
                    raise Exception('无法创建对话')

                chatId = str(chat['_id'])

            handler = StreamChatHandler(
                userId=userId, 
                chatId=chatId, 
                userMessage=userMessage
            )

            return handler.processStream()
        except Exception as e:
            logging.error(f'❌ 处理用户消息失败: { str(e) }')
            return flask.jsonify({
                'code': 500,
                'message': f'处理用户消息失败: { str(e) }'
            }), 500

    # 获取对话的消息历史
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.CHAT_MESSAGES['route'], methods=ApiState.CHAT_MESSAGES['method'])
    @UserTokenHelper.userTokenRequired
    def getChatMessages(chatId: str):
        try:
            user = flask.g.user
            userId = str(user['_id'])
            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (not chat or str(chat['userId']) != userId):
                return flask.jsonify({
                    'code': 404,
                    'message': '对话不存在或无权限'
                }), 404
            
            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 50))
            messages = MongoDBConfig.messageManager.getMessagesList(chatId, page, limit)

            return flask.jsonify({
                'code': 0,
                'message': '获取对话消息成功',
                'data': {
                    'chat': chat,
                    'messages': messages,
                    'page': page,
                    'limit': limit
                }
            }), 200
        except Exception as e:
            logging.error(f'❌ 获取对话消息历史失败: { str(e) }')
            return flask.jsonify({
                'code': 500,
                'message': f'获取对话消息历史失败: { str(e) }'
            }), 500
        
    # 获取用户的对话列表
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.CHAT_LIST['route'], methods=ApiState.CHAT_LIST['method'])
    @UserTokenHelper.userTokenRequired
    def getUserChatsList():
        try:
            user = flask.g.user
            userId = str(user['_id'])
            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 20))
            chats = MongoDBConfig.chatManager.getUserChats(userId, page, limit)

            return flask.jsonify({
                'code': 0,
                'message': '获取用户对话列表成功',
                'data': {
                    'chats': chats,
                    'page': page,
                    'limit': limit
                }
            }), 200
        except Exception as e:
            logging.error(f'❌ 获取用户对话列表失败: { str(e) }')
            return flask.jsonify({
                'code': 500,
                'message': f'获取用户对话列表失败: { str(e) }'
            }), 500

