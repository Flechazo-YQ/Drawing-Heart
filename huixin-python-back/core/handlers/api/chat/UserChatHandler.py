import logging, flask, datetime

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.api.chat.StreamChatHandler import StreamChatHandler
from core.states.GlobalState import GlobalState
from core.states.SocketState import SocketState

from flask import Response
from typing import Final

class UserChatHandler:
    DANGER_KEYWORDS: Final[list[str]] = ['自杀', '自残', '死', '想死', '活不下去', '结束生命', '轻生']

    # 创建新对话
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats', methods=['POST'])
    def createNewChat():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({
                'message': 'Token is missing!'
            }), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({
                'message': 'Invalid token!'
            }), 401

        try:
            data = flask.request.get_json()

            # 初始标题设为空, 等第一条消息后再更新
            title = data.get('title', '')
            chatType = data.get('type', 'normal')  # 新增：支持传入对话类型
            chatId = MongoDBConfig.chatManager.createChat(userId, title, chatType)

            # 设置为当前活跃聊天 - 统一使用字符串类型用户ID
            GlobalState.userCurrentChats[userId] = chatId

            # 清除用户的当前上下文, 开始新对话
            GlobalState.userContexts[userId] = []

            logging.info(f'用户 { userId } 创建新对话: { chatId }')

            return flask.jsonify({
                'code': 0,
                'message': '创建对话成功',
                'data': {
                    'chat_id': chatId,
                    'title': title if title else '新对话'
                }
            })
        
        except Exception as e:
            logging.error(f'创建新对话错误: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'创建新对话失败: { str(e) }'
            }), 500
        
    # 隐藏对话(软删除)
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/<chatId>', methods=['DELETE'])
    def hideChat(chatId: str):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({
                'message': 'Token is missing!'
            }), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({
                'message': 'Invalid token!'
            }), 401

        try:
            # 验证对话是否属于当前用户
            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (not chat or chat['user_id'] != userId):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404

            success = MongoDBConfig.chatManager.hideChat(chatId)

            if (not success):
                return flask.jsonify({
                    'code': 1,
                    'message': '删除对话失败'
                }), 500
            
            return flask.jsonify({
                'code': 0,
                'message': '删除对话成功'
            })
            
        except Exception as e:
            logging.error(f'删除对话错误: { str(e) }')
            
            return flask.jsonify({
                'code': 1,
                'message': f'删除对话失败: { str(e) }'
            }), 500
        
    # 删除对话(硬删除)
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/<chatId>/delete', methods=['DELETE'])
    def deleteChat(chatId: str):
        token = flask.request.headers.get('Authorization')
        
        if (not token):
            return flask.jsonify({
                'message': 'Token is missing!'
            }), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({
                'code': 401,
                'message': 'Invalid token!'
            }), 401

        try:
            success = MongoDBConfig.chatManager.deleteChat(chatId, userId)

            if (not success):
                return flask.jsonify({
                    'code': 404,
                    'message': '删除失败, 对话不存在或无权限'
                }), 404
            
            return flask.jsonify({
                'code': 0,
                'message': '对话删除成功'
            })
        except Exception as e:
            logging.error(f'删除对话错误: { str(e) }')

            return flask.jsonify({
                'code': 500,
                'message': f'删除对话失败: { str(e) }'
            }), 500

    # 获取对话的消息历史
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/<chatId>/messages', methods=['GET'])
    def getChatMessages(chatId: str):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (not chat or chat['user_id'] != userId):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404

            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 50))

            # 使用新的方法获取完整对话和消息
            fullChat = MongoDBConfig.messageManager.getChatWithMessages(chatId)

            if (not fullChat):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在'
                }), 404

            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 50))

            # 使用新的方法获取完整对话和消息
            fullChat = MongoDBConfig.messageManager.getChatWithMessages(chatId)

            if (not fullChat):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在'
                }), 404

            allMessages = fullChat.get('messages', [])

            # 分页处理
            startIndex = (page - 1) * limit
            endIndex = startIndex + limit
            messages = allMessages[startIndex : endIndex]

            # 如果需要分组消息(用于可折叠显示)
            if (not messages):
                return flask.jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'chat': {
                            '_id': fullChat['_id'],
                            'title': fullChat['title'],
                            'created_at': fullChat['created_at'],
                            'updated_at': fullChat['updated_at'],
                            'message_count': fullChat['message_count']
                        },
                        'messages': messages,
                        'total_messages': len(allMessages)
                    }
                })
            
            groupedMessages = []
            currentGroup = None

            for msg in messages:
                if (currentGroup is None or currentGroup['sender'] != msg['sender']):

                    # 开始新的消息组
                    currentGroup = {
                        'sender': msg['sender'],
                        'timestamp': msg['timestamp'],
                        'messages': [msg],
                        'collapsed': False  # 默认展开
                    }
                    groupedMessages.append(currentGroup)
                else:

                    # 添加到当前组
                    if (not isinstance(currentGroup['messages'], list)):
                        currentGroup['messages'] = [msg]
                    else:
                        currentGroup['messages'].append(msg)

                    currentGroup['timestamp'] = msg['timestamp']  # 更新为最新时间

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'chat': {
                        '_id': fullChat['_id'],
                        'title': fullChat['title'],
                        'created_at': fullChat['created_at'],
                        'updated_at': fullChat['updated_at'],
                        'message_count': fullChat['message_count']
                    },
                    'messages': groupedMessages,
                    'total_groups': len(groupedMessages),
                    'total_messages': len(allMessages)
                }
            })
                
        except Exception as e:
            logging.error(f'获取消息历史错误: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'获取消息历史失败: { str(e) }'
            }), 500
        
    # 加载对话上下文
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/<chatId>/load', methods=['POST'])
    def loadChatContext(chatId: str):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (not chat or chat['user_id'] != userId):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404
            
            # 设置为当前活跃聊天 - 统一使用字符串类型用户ID
            GlobalState.userCurrentChats[userId] = chatId

            # 获取最近的消息作为上下文
            recentMessages = MongoDBConfig.messageManager.getLatestMessages(chatId, 10)

            logging.info(f'用户 { userId } 切换到对话: { chatId }')

            # 更新用户特定的上下文(userId已在上面定义)
            GlobalState.userContexts[userId] = []

            for msg in recentMessages:
                if (msg['sender'] == 'user'):
                    GlobalState.userContexts[userId].append({
                        'role': 'user',
                        'content': msg['content']
                    })
                elif (msg['sender'] == 'assistant'):
                    GlobalState.userContexts[userId].append({
                        'role': 'assistant', 
                        'content': msg['content']
                    })
            
            return flask.jsonify({
                'code': 0,
                'message': '对话上下文加载成功',
                'data': {
                    'chat': chat,
                    'context_loaded': len(GlobalState.userContexts[userId])
                }
            })
        
        except Exception as e:
            logging.error(f'加载对话上下文错误: { str(e) }')
            return flask.jsonify({
                'code': 1,
                'message': f'加载对话上下文失败: { str(e) }'
            }), 500
        
    # 切换消息组的折叠状态
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/<chatId>/toggle-group', methods=['POST'])
    def toggleMessageGroup(chatId: str):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = MongoDBConfig.chatManager.getChatById(chatId)

            if (not chat or chat['user_id'] != userId):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404

            data = flask.request.get_json()
            groupIndex = data.get('group_index')
            collapsed = data.get('collapsed', False)
            
            # 这里可以将折叠状态保存到用户偏好设置中
            # 目前只返回成功响应, 前端可以本地管理状态

            return flask.jsonify({
                'code': 0,
                'message': '状态更新成功',
                'data': {
                    'group_index': groupIndex,
                    'collapsed': collapsed
                }
            })
        except Exception as e:
            logging.error(f'切换消息组状态错误: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'操作失败: { str(e) }'
            }), 500

    # 处理用户消息
    @staticmethod
    def processMessage(message):
        dangerous = 0.0  # 声明局部变量
        
        try:
            logging.info(f'🔍 开始检测消息危险性: { message[:50] }...')
            
            # 先检查明显的危险关键词
            hasDangerKeyword = any(keyword in message for keyword in UserChatHandler.DANGER_KEYWORDS)

            if (hasDangerKeyword):
                logging.warning(f'🚨 检测到危险关键词: { message }')
                dangerous = 0.9  # 强制设置为高危险级别
                label = '危险'
            else:
                # 使用模型进行预测
                classifier = GlobalState.CLASSIFIER  # 获取分类器实例

                if (not classifier):
                    logging.error('❌ 分类器未初始化')
                    return 0.0

                label, probs = classifier.predict(message) # type: ignore
                # probs是一个数组[危险概率, 负面概率, 其他概率]
                # 根据模型定义：0: '危险', 1: '负面', 2: '其他'
                dangerous = float(probs[0])  # 确保是 float 类型
            
            logging.info(f'🎯 危险检测结果: label={ label }, dangerous_prob={ dangerous:.4f}')

            return dangerous
        except Exception as e:
            logging.error(f'❌ 情感分析模型预测失败: { str(e) }')

            # 如果模型预测失败, 但包含危险关键词, 仍然标记为危险
            dangerous = 0.9 if any(keyword in message for keyword in UserChatHandler.DANGER_KEYWORDS) else 0.0

            return dangerous
        
    # 流式聊天接口(AI对话)
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/stream', methods=['POST'])
    def streamChat():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({
                'message': 'Token is missing!'
            }), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({
                'message': 'Invalid token!'
            }), 401

        user = MongoDBConfig.userManager.getUserById(userId)

        if (not user):
            logging.error(f"❌ 严重错误: Token有效, 但无法在数据库中找到用户 { userId }")
            return flask.jsonify({
                'message': '用户不存在'
            }), 404
        
        userName = user.get('username', '未知用户')
        data = flask.request.json

        if (not data):
            return flask.jsonify({
                'message': '请求数据不能为空!'
            }), 400
        
        userMessage = data.get('message', '')

        logging.info(f'📝 开始处理用户 { userName } ({ userId }) 的消息: { userMessage[:30] }...')
        
        dangerousProb = UserChatHandler.processMessage(userMessage)

        logging.info(f'🔍 消息危险性检测结果: { dangerousProb }')

        currentChatId = GlobalState.userCurrentChats.get(userId)

        if (not currentChatId):
            chatType = 'dangerous' if (dangerousProb > 0.5) else 'normal'
            currentChatId = MongoDBConfig.chatManager.createChat(userId, '新对话', chatType)
            
            GlobalState.userCurrentChats[userId] = currentChatId
            logging.info(f'为用户 { userName } ({ userId }) 创建新对话: { currentChatId }')
        else:
            logging.info(f'用户 { userName } ({ userId }) 使用当前对话: { currentChatId }')

        streamHandler = StreamChatHandler(
            userId=userId,
            userName=userName,
            userMessage=userMessage,
            dangerous=dangerousProb,
            currentChatId=currentChatId,
            userContext=GlobalState.userContexts.get(userId, [])
        )

        if (dangerousProb > 0.3):
            logging.warning(f"🚨 检测到高危消息！准备转接人工。用户: { userName }, 对话ID: { currentChatId }")

            transferData = {
                'userId': userId,
                'userName': userName,
                'chatId': currentChatId,
                'message': userMessage,
                'dangerProb': dangerousProb,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }

            task = {
                'event': 'human_transfer_request',
                'data': transferData
            }
            SocketState.socketioTaskQueue.put(task)
            logging.info(f"🔔 已发送人工干预请求给管理员, 用户: { userName }, 对话ID: { currentChatId }")
            return streamHandler.handleDangerousMessage()
        
        streamHandler.handleNormalMessage()

        payload = streamHandler.generateAIPayload()

        return Response(
            flask.stream_with_context(streamHandler.generateAIMessage(payload)),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )

    # 清除用户聊天上下文
    @staticmethod
    @BlueprintConfig.apiRoutes('/clear/chats/context', methods=['POST'])
    def clearChatContext():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401
            
        try:            
            # 清除用户特定的上下文
            if (userId in GlobalState.userContexts):
                GlobalState.userContexts[userId] = []

            # 如果用户在危险对话列表中, 清除其记录
            if (userId in GlobalState.dangerousChats):
                del GlobalState.dangerousChats[userId]

            # 清除用户的最新图片URL
            if (userId in GlobalState.userLatestImages):
                del GlobalState.userLatestImages[userId]

            # 注意：不再清除全局text_result, 因为现在使用数据库中的分析结果
            
            return flask.jsonify({
                'code': 0,
                'message': '聊天上下文已清除'
            }), 200
            
        except Exception as e:
            print(f'清除聊天上下文错误: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'清除聊天上下文失败: { str(e) }'
            }), 500
        
    # 清除用户当前活跃聊天, 下次对话将创建新的聊天
    @staticmethod
    @BlueprintConfig.apiRoutes('/clear/chats/current', methods=['POST'])
    def clearCurrentChat():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:            
            # 清除用户的当前活跃聊天
            if (userId in GlobalState.userCurrentChats):
                oldChatId = GlobalState.userCurrentChats[userId]

                del GlobalState.userCurrentChats[userId]
                logging.info(f'清除用户 { userId } 的当前聊天: { oldChatId }')

            # 清除用户的上下文
            if (userId in GlobalState.userContexts):
                GlobalState.userContexts[userId] = []

            return flask.jsonify({
                'code': 0,
                'message': '已清除当前聊天, 下次对话将创建新的聊天'
            })
        
        except Exception as e:
            logging.error(f'清除当前聊天失败: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'清除当前聊天失败: { str(e) }'
            }), 500
        
    # 获取用户的对话列表
    @staticmethod
    @BlueprintConfig.apiRoutes('/chats/list', methods=['GET'])
    def getUserChats():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 20))
            chats = MongoDBConfig.chatManager.getUserChats(userId, page, limit)

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': chats
            })
        except Exception as e:
            logging.error(f"获取对话列表错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取对话列表失败: { str(e) }'
            }), 500
