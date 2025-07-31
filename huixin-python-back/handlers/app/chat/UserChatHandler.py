import logging, flask, requests, json, threading, datetime

from handlers.token.UserTokenHandler import UserTokenHandler
from states.GlobalState import GlobalState
from states.SocketState import SocketState

from mongodb_config import chat_manager, message_manager, drawing_analysis_manager

from flask import Response

class UserChatHandler:

    # 创建新对话
    @staticmethod
    @GlobalState.app.route('/api/chats', methods=['POST'])
    def createNewChat():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            data = flask.request.get_json()

            # 初始标题设为空，等第一条消息后再更新
            title = data.get('title', '')
            chatType = data.get('type', 'normal')  # 新增：支持传入对话类型

            chatId = chat_manager.create_chat(userId[0], title, chatType)

            # 设置为当前活跃聊天 - 统一使用字符串类型用户ID
            userIdString = str(userId[0])
            GlobalState.userCurrentChats[userIdString] = chatId

            # 清除用户的当前上下文，开始新对话
            GlobalState.userContexts[userIdString] = []

            logging.info(f"用户 { userIdString } 创建新对话: { chatId }")

            return flask.jsonify({
                'code': 0,
                'message': '创建对话成功',
                'data': {
                    'chat_id': chatId,
                    'title': title if title else '新对话'
                }
            })
        
        except Exception as e:
            logging.error(f"创建新对话错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'创建新对话失败: { str(e) }'
            }), 500
        
    # 隐藏对话(软删除)
    @staticmethod
    @GlobalState.app.route('/api/chats/<chat_id>', methods=['DELETE'])
    def hideChat(chatId):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = chat_manager.get_chat_by_id(chatId)

            if (not chat or chat['user_id'] != userId[0]):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404

            success = chat_manager.hide_chat(chatId)

            if (success):
                return flask.jsonify({
                    'code': 0,
                    'message': '删除对话成功'
                })
            else:
                return flask.jsonify({
                    'code': 1,
                    'message': '删除对话失败'
                }), 500
            
        except Exception as e:
            logging.error(f"删除对话错误: {str(e)}")
            
            return flask.jsonify({
                'code': 1,
                'message': f'删除对话失败: {str(e)}'
            }), 500
        
    # 获取对话的消息历史
    @staticmethod
    @GlobalState.app.route('/api/chats/<chat_id>/messages', methods=['GET'])
    def getChatMessages(chat_id):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = chat_manager.get_chat_by_id(chat_id)
            if not chat or chat['user_id'] != userId[0]:
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404

            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 50))
            group_messages = flask.request.args.get('group', 'false').lower() == 'true'

            # 使用新的方法获取完整对话和消息
            full_chat = message_manager.get_chat_with_messages(chat_id)
            if not full_chat:
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在'
                }), 404
            
            all_messages = full_chat.get('messages', [])
            
            # 分页处理
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            messages = all_messages[start_idx:end_idx]
            
            # 如果需要分组消息（用于可折叠显示）
            if group_messages:
                grouped_messages = []
                current_group = None
                
                for msg in messages:
                    if current_group is None or current_group['sender'] != msg['sender']:
                        # 开始新的消息组
                        current_group = {
                            'sender': msg['sender'],
                            'timestamp': msg['timestamp'],
                            'messages': [msg],
                            'collapsed': False  # 默认展开
                        }
                        grouped_messages.append(current_group)
                    else:
                        # 添加到当前组
                        current_group['messages'].append(msg)
                        current_group['timestamp'] = msg['timestamp']  # 更新为最新时间

                return flask.jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'chat': {
                            '_id': full_chat['_id'],
                            'title': full_chat['title'],
                            'created_at': full_chat['created_at'],
                            'updated_at': full_chat['updated_at'],
                            'message_count': full_chat['message_count']
                        },
                        'messages': grouped_messages,
                        'total_groups': len(grouped_messages),
                        'total_messages': len(all_messages)
                    }
                })
            else:
                return flask.jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'chat': {
                            '_id': full_chat['_id'],
                            'title': full_chat['title'],
                            'created_at': full_chat['created_at'],
                            'updated_at': full_chat['updated_at'],
                            'message_count': full_chat['message_count']
                        },
                        'messages': messages,
                        'total_messages': len(all_messages)
                    }
                })
        except Exception as e:
            logging.error(f"获取消息历史错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取消息历史失败: { str(e) }'
            }), 500
        
    # 加载对话上下文
    @staticmethod
    @GlobalState.app.route('/api/chats/<chat_id>/load', methods=['POST'])
    def loadChatContext(chatId):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = chat_manager.get_chat_by_id(chatId)

            if (not chat or chat['user_id'] != userId[0]):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404
            
            # 设置为当前活跃聊天 - 统一使用字符串类型用户ID
            userIdString = str(userId[0])
            GlobalState.userCurrentChats[userIdString] = chatId

            # 获取最近的消息作为上下文
            recent_messages = message_manager.get_latest_messages(chatId, 10)

            logging.info(f"用户 {userIdString} 切换到对话: {chatId}")

            # 更新用户特定的上下文(userIdString已在上面定义)
            GlobalState.userContexts[userIdString] = []

            for msg in recent_messages:
                if msg['sender'] == 'user':
                    GlobalState.userContexts[userIdString].append({
                        "role": "user",
                        "content": msg['content']
                    })
                elif msg['sender'] == 'assistant':
                    GlobalState.userContexts[userIdString].append({
                        "role": "assistant", 
                        "content": msg['content']
                    })
            
            return flask.jsonify({
                'code': 0,
                'message': '对话上下文加载成功',
                'data': {
                    'chat': chat,
                    'context_loaded': len(GlobalState.userContexts[userIdString])
                }
            })
        
        except Exception as e:
            logging.error(f"加载对话上下文错误: {str(e)}")
            return flask.jsonify({
                'code': 1,
                'message': f'加载对话上下文失败: {str(e)}'
            }), 500
        
    # 切换消息组的折叠状态
    @staticmethod
    @GlobalState.app.route('/api/chats/<chat_id>/toggle-group', methods=['POST'])
    def toggleMessageGroup(chat_id):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 验证对话是否属于当前用户
            chat = chat_manager.get_chat_by_id(chat_id)

            if (not chat or chat['user_id'] != userId[0]):
                return flask.jsonify({
                    'code': 1,
                    'message': '对话不存在或无权限'
                }), 404

            data = flask.request.get_json()
            groupIndex = data.get('group_index')
            collapsed = data.get('collapsed', False)
            
            # 这里可以将折叠状态保存到用户偏好设置中
            # 目前只返回成功响应，前端可以本地管理状态

            return flask.jsonify({
                'code': 0,
                'message': '状态更新成功',
                'data': {
                    'group_index': groupIndex,
                    'collapsed': collapsed
                }
            })
        except Exception as e:
            logging.error(f"切换消息组状态错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'操作失败: { str(e) }'
            }), 500

    @staticmethod
    def processMessage(message):
        global dangerous
        label, dangerous = classifier.predict(message)
        dangerous = dangerous[0]
        return dangerous
        
    # 流式聊天接口(AI对话)
    @classmethod
    @GlobalState.app.route('/api/stream-chat', methods=['POST'])
    def streamChat(cls):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        user = flask.request.json

        if (not user):
            return Response("Invalid JSON or missing request body", status=400)
        
        userMessage = user.get('message', '')

        # 检测消息是否危险
        thread = threading.Thread(target=cls.processMessage, args=(userMessage,))
        thread.start()
        thread.join()  # 等待线程完成
        
        # 获取或创建当前聊天 - 统一使用字符串类型的用户ID
        userIdString = str(userId[0])
        currentChatId = GlobalState.userCurrentChats.get(userIdString)

        if (not currentChatId):

            # 如果没有当前聊天，根据消息危险性创建不同类型的对话
            chatType = "dangerous" if dangerous > 0.5 else "normal"
            currentChatId = chat_manager.create_chat(userId[0], "新对话", chatType)
            GlobalState.userCurrentChats[userIdString] = currentChatId

            logging.info(f"为用户 { userIdString } 创建新对话: { currentChatId }")
        else:
            logging.info(f"用户 { userIdString } 使用现有对话: { currentChatId }")

        # 如果检测到危险消息，更新对话类型
        if dangerous > 0.5:
            # 更新现有对话为危险类型
            chat_manager.update_chat(currentChatId, {"type": "dangerous"})
            
            print('检测到危险消息，需要人工干预:', userMessage)
            # 将聊天内容记录到危险对话字典（userIdStr已在上面定义）

            # 获取用户的上下文
            user_context = GlobalState.userContexts.get(userIdString, [])

            if (userIdString not in GlobalState.dangerousChats):
                # 初始化用户的危险聊天记录
                GlobalState.dangerousChats[userIdString] = {
                    'username': userId[1],
                    'chat_id': currentChatId,  # 添加chat_id以便后续消息保存到数据库
                    'messages': user_context.copy() + [
                        {"role": "user", "content": userMessage}
                    ],
                    'is_active': True,
                    'admin_id': None,
                    'last_updated': datetime.datetime.now().isoformat()
                }
            else:
                # 更新现有聊天记录
                GlobalState.dangerousChats[userIdString]['messages'].append({
                    "role": "user", 
                    "content": userMessage
                })
                GlobalState.dangerousChats[userIdString]['last_updated'] = datetime.datetime.now().isoformat()

            # 保存用户消息到MongoDB
            try:
                message_manager.add_message(
                    chat_id=currentChatId,
                    message_type="text",
                    content=userMessage,
                    sender="user",
                    danger_level=dangerous
                )
            except Exception as e:
                logging.error(f"保存危险消息失败: {str(e)}")
            
            # 通知所有在线管理员有新的危险对话
            SocketState.socketio.emit('dangerous_chat_alert', {
                'user': {
                    'userId': userIdString,
                    'username': userId[1],
                    'lastMessage': userMessage
                }
            }, room='admin_room')
            
            # 检查是否有管理员在线
            admin_message = "系统检测到您的内容可能存在风险，已切换到人工客服模式。请稍等片刻，管理员正在审核您的对话..."
            
            # 添加系统消息到危险对话记录
            GlobalState.dangerousChats[userIdString]['messages'].append({
                "role": "admin", 
                "content": admin_message,
                "time": datetime.datetime.now().isoformat(),
                "is_system": True,
                "messageId": "system_risk_alert"  # 添加固定messageId用于前端去重
            })
            
            # 保存系统消息到MongoDB
            try:
                message_manager.add_message(
                    chat_id=currentChatId,
                    message_type="text",
                    content=admin_message,
                    sender="system",
                    danger_level=dangerous
                )
            except Exception as e:
                logging.error(f"保存系统消息失败: {str(e)}")
            
            # 返回一个固定提示
            return admin_message
        
        # 如果消息不危险，正常处理
        # 每次对话都重新获取用户在当日或4小时内的最新绘画分析结果
        latest_analysis = None
        analysis_fetch_time = datetime.datetime.utcnow()
        
        try:
            logging.info(f"开始获取用户 {userId[0]} 的最新分析结果...")

            # 首先尝试获取当日的分析结果
            latestAnalysis = drawing_analysis_manager.get_recent_analysis(userId[0], hours=0)

            if (not latestAnalysis):
                # 如果当日没有分析结果，尝试获取4小时内的分析结果
                latestAnalysis = drawing_analysis_manager.get_recent_analysis(userId[0], hours=4)

            if (latestAnalysis):
                analysis_date = latestAnalysis['analysis_date']
                analysis_time = latestAnalysis['created_at']
                analysis_id = latestAnalysis.get('_id', 'unknown')
                logging.info(f"✅ 成功获取用户 {userId[0]} 的分析结果 - ID: {analysis_id}, 日期: {analysis_date}, 创建时间: {analysis_time}")
            else:
                logging.info(f"ℹ️  用户 {userId[0]} 在当日或4小时内暂无分析记录")
        except Exception as e:
            logging.error(f"❌ 获取用户 {userId[0]} 的分析结果失败: {str(e)}")

        # 构建系统消息 - 完全基于数据库中的最新分析结果
        if (latestAnalysis):
            analysisDate = latestAnalysis['analysis_date']
            analysisResult = latestAnalysis['analysis_result']
            systemContent = f"你现在是一名心理医师，你的名字叫绘心同学。用户在{ analysisDate }完成了心理绘画测试，以下是最新的分析结果：{ analysisResult } \n\n请结合这个分析结果帮助用户，用通俗易懂的语言与用户交流，用多轮对话的形式，每次别说太多。如果用户的问题与绘画分析相关，请参考分析结果给出建议。"
            logging.info(f"🎯 AI将基于 { analysisDate } 的分析结果进行对话")
        else:
            # 如果没有符合时间条件的分析结果，不参考任何分析内容
            systemContent = "你现在是一名心理医师，你的名字叫绘心同学。请用温暖、专业的语言与用户交流，用多轮对话的形式，每次别说太多。如果用户需要心理绘画分析，请引导他们先完成绘画测试。"
            logging.info("🔄 AI将不参考任何分析结果进行对话（无符合时间条件的分析）")
        
        # 获取用户的上下文
        user_id_str = str(userId[0])
        user_context = GlobalState.userContexts.get(user_id_str, [])
        
        messages = [
            {
                "content": systemContent,
                "role": "system"
            }
        ] + user_context.copy() + [
            {"content": userMessage, "role": "user"}
        ]
        payload = {
            "model": "Pro/deepseek-ai/DeepSeek-V3",
            "stream": True,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "stop": [],
            "messages": messages
        }
        headers = {
            "Authorization": "Bearer sk-bhgbmuxblqtroypztkuonssqqkitngencupdofitajnmvbtv",
            "Content-Type": "application/json"
        }

        def generate():
            assistant_reply = ''
            try:
                # 先保存用户消息到MongoDB
                user_message_id = message_manager.add_message(
                    chat_id=currentChatId,
                    message_type="text",
                    content=userMessage,
                    sender="user"
                )
                
                # 发起 POST 请求，启用流式响应
                with requests.post(GlobalState.url, json=payload, headers=headers, stream=True) as response:
                    response.raise_for_status()  # 检查响应状态码
                    response.encoding = 'utf-8'  # 明确指定编码

                    # 逐行读取响应内容
                    for line in response.iter_lines(decode_unicode=True):
                        if (line):  # 跳过空行

                            # 假设 API 返回的是 SSE 格式，每行以 "data: " 开头
                            if (line.startswith("data: ")):
                                try:
                                    # 提取数据部分并解析为 JSON
                                    data = line[len("data: "):].strip()

                                    if (data == "[DONE]"):
                                        # 如果遇到 [DONE]，结束生成器
                                        break
                                    jsonData = json.loads(data)

                                    # 提取所需字段（根据 API 响应格式调整）
                                    # 假设响应中有 'choices[0]['delta']['content']'
                                    content = jsonData.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    assistantReply += content

                                    if (content):
                                        yield f"{content}"
                                except json.JSONDecodeError:
                                    # 如果 JSON 解析失败，记录错误（或跳过）
                                    print(f"Failed to parse JSON: { line }")
                
                # 成功获取完整回复后保存助手消息到MongoDB
                if (assistantReply):
                    assistant_message_id = message_manager.add_message(
                        chat_id=currentChatId,
                        message_type="text",
                        content=assistantReply,
                        sender="assistant"
                    )
                
                # 更新用户特定的上下文
                if (user_id_str not in GlobalState.userContexts):
                    GlobalState.userContexts[user_id_str] = []

                GlobalState.userContexts[user_id_str].extend([
                    {"role": "user", "content": userMessage},
                    {"role": "assistant", "content": assistantReply}
                ])

                # 保留最多5轮对话（10条消息）
                if (len(GlobalState.userContexts[user_id_str]) > 10):
                    GlobalState.userContexts[user_id_str] = GlobalState.userContexts[user_id_str][-10:]

                # 始终更新对话标题为用户的最新消息（对话结束前的最后一条语言）
                try:
                    # 截取用户消息的前20个字符作为标题
                    new_title = userMessage[:20] + "..." if len(userMessage) > 20 else userMessage
                    chat_manager.update_chat_title(currentChatId, new_title)

                except Exception as e:
                    logging.error(f"更新对话标题失败: {str(e)}")
                    
            except requests.RequestException as e:
                # 处理请求异常，例如网络错误或 API 返回错误状态码
                yield f"data: Error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                # 处理其他异常，如数据库保存错误
                logging.error(f"聊天处理错误: {str(e)}")
                yield f"data: Error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        # 返回流式响应
        return Response(
            flask.stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )

    #清除用户聊天上下文
    @staticmethod
    @GlobalState.app.route('/api/clear-chat-context', methods = ['POST'])
    def clearChatContext():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401
            
        try:
            userIdString = str(userId[0])
            
            # 清除用户特定的上下文
            if (userIdString in GlobalState.userContexts):
                GlobalState.userContexts[userIdString] = []

            # 如果用户在危险对话列表中，清除其记录
            if (userIdString in GlobalState.dangerousChats):
                del GlobalState.dangerousChats[userIdString]

            # 清除用户的最新图片URL
            if (userIdString in GlobalState.userLatestImages):
                del GlobalState.userLatestImages[userIdString]

            # 注意：不再清除全局text_result，因为现在使用数据库中的分析结果
            
            return flask.jsonify({
                'code': 0,
                'message': '聊天上下文已清除'
            }), 200
            
        except Exception as e:
            print(f"清除聊天上下文错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'清除聊天上下文失败: { str(e) }'
            }), 500
        
    #清除用户当前活跃聊天, 下次对话将创建新的聊天
    @staticmethod
    @GlobalState.app.route('/api/clear-current-chat', methods=['POST'])
    def clearCurrentChat():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            userIdString = str(userId[0])
            
            # 清除用户的当前活跃聊天
            if (userIdString in GlobalState.userCurrentChats):
                oldChatId = GlobalState.userCurrentChats[userIdString]

                del GlobalState.userCurrentChats[userIdString]
                logging.info(f"清除用户 { userIdString } 的当前聊天: { oldChatId }")

            # 清除用户的上下文
            if (userIdString in GlobalState.userContexts):
                GlobalState.userContexts[userIdString] = []

            return flask.jsonify({
                'code': 0,
                'message': '已清除当前聊天，下次对话将创建新的聊天'
            })
        
        except Exception as e:
            logging.error(f"清除当前聊天失败: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'清除当前聊天失败: { str(e) }'
            }), 500