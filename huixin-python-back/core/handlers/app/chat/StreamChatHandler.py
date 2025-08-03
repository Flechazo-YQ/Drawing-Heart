import flask, requests, json, logging, datetime

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.GlobalState import GlobalState
from core.states.SocketState import SocketState

from flask import Response
from typing import Final

class StreamChatHandler:
    ADMINMESSAGE: Final[str] = '系统检测到您的内容可能存在风险, 已切换到人工客服模式。请稍等片刻, 管理员正在审核您的对话...'
    HEADERS: Final[dict[str, str]] = {
        "Authorization": "Bearer sk-bhgbmuxblqtroypztkuonssqqkitngencupdofitajnmvbtv",
        "Content-Type": "application/json"
    }

    def __init__(self, userId, userIdString, userName, userMessage, dangerous, currentChatId, userContext):
        self.userId = userId
        self.userIdString = userIdString
        self.userName = userName
        self.userMessage = userMessage
        self.dangerous = dangerous
        self.currentChatId = currentChatId
        self.userContext = userContext

    # 处理危险消息
    def handleDangerousMessage(self):
        logging.warning(f"🚨 触发危险检测: dangerous={self.dangerous:.4f} > 0.3")
        MongoDBConfig.chatManager.updateChat(self.currentChatId, {"type": "dangerous"})

        logging.warning(f'🚨 检测到危险消息, 需要人工干预: {self.userMessage }')
        userContext = GlobalState.userContexts.get(self.userIdString, [])

        if (self.userIdString not in GlobalState.dangerousChats):
            GlobalState.dangerousChats[self.userIdString] = {
                'username': self.userName,
                'chat_id': self.currentChatId,
                'messages': userContext.copy() + [
                    { 
                        "role": "user", 
                        "content": self.userMessage 
                    }
                ],
                'is_active': True,
                'admin_id': None,
                'last_updated': datetime.datetime.now().isoformat()
            }
        else:
            GlobalState.dangerousChats[self.userIdString]['messages'].append({
                "role": "user",
                "content": self.userMessage
            })
            GlobalState.dangerousChats[self.userIdString]['last_updated'] = datetime.datetime.now().isoformat()

        # 保存用户消息到MongoDB
        try:
            MongoDBConfig.messageManager.addMessage(
                chatId=self.currentChatId,
                messageType="text",
                content=self.userMessage,
                sender="user",
                dangerLevel=self.dangerous
            )
        except Exception as e:
            logging.error(f"保存危险消息失败: { str(e) }")
        
        # 通知所有在线管理员有新的危险对话
        logging.info(f"🔔 准备通知管理员危险对话, 用户id: { self.userIdString }")
        SocketState.socketio.emit(
            'dangerous_chat_alert', 
            {
                'user': {
                    'userId': self.userIdString,
                    'username': self.userName,
                    'lastMessage': self.userMessage
                }
            }, 
            room='admin_room' # type: ignore
        )
        logging.info(f"✅ 已发送危险对话通知到管理员房间")
        
        # 添加系统消息到危险对话记录
        GlobalState.dangerousChats[self.userIdString]['messages'].append({
            "role": "admin", 
            "content": StreamChatHandler.ADMINMESSAGE,
            "time": datetime.datetime.now().isoformat(),
            "is_system": True,
            "messageId": "system_risk_alert"  # 添加固定messageId用于前端去重
        })
        
        # 保存系统消息到MongoDB
        try:
            MongoDBConfig.messageManager.addMessage(
                chatId=self.currentChatId,
                messageType="text",
                content=StreamChatHandler.ADMINMESSAGE,
                sender="system",
                dangerLevel=self.dangerous
            )
        except Exception as e:
            logging.error(f"保存系统消息失败: { str(e) }")

        return Response(
            flask.stream_with_context(self.generateAdminMessage()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
    
    # 处理正常消息
    def handleNormalMessage(self):
        latestAnalysis = None
        
        try:
            logging.info(f"开始获取用户 { self.userId[0] } 的最新分析结果...")
            
            # 首先尝试获取当日的分析结果
            latestAnalysis = MongoDBConfig.drawingAnalysisManager.getRecentAnalysis(self.userId[0], hours=0)

            if (not latestAnalysis):
                # 如果当日没有分析结果, 尝试获取4小时内的分析结果
                latestAnalysis = MongoDBConfig.drawingAnalysisManager.getRecentAnalysis(self.userId[0], hours=4)
                logging.info(f"ℹ️  用户 { self.userId[0] } 在当日或4小时内暂无分析记录")

                # 如果没有符合时间条件的分析结果, 不参考任何分析内容
                self.systemContent = "你现在是一名心理医师, 你的名字叫绘心同学。请用温暖、专业的语言与用户交流, 用多轮对话的形式, 每次别说太多。如果用户需要心理绘画分析, 请引导他们先完成绘画测试。"
                logging.info("🔄 AI将不参考任何分析结果进行对话（无符合时间条件的分析）")
            else:
                analysisDate = latestAnalysis['analysis_date']
                analysisTime = latestAnalysis['created_at']
                analysisId = latestAnalysis.get('_id', 'unknown')
                logging.info(f"✅ 成功获取用户 { self.userId[0] } 的分析结果 - ID: { analysisId }, 日期: { analysisDate }, 创建时间: { analysisTime }")

                analysisResult = latestAnalysis['analysis_result']
                self.systemContent = f"你现在是一名心理医师, 你的名字叫绘心同学。用户在{ analysisDate }完成了心理绘画测试, 以下是最新的分析结果：{ analysisResult } \n\n请结合这个分析结果帮助用户, 用通俗易懂的语言与用户交流, 用多轮对话的形式, 每次别说太多。如果用户的问题与绘画分析相关, 请参考分析结果给出建议。"
                logging.info(f"🎯 AI将基于 { analysisDate } 的分析结果进行对话")

        except Exception as e:
            logging.error(f"❌ 获取用户 { self.userId[0] } 的分析结果失败: { str(e) }")

    # 返回流式格式的管理员信息
    def generateAdminMessage(self):
        for char in self.ADMINMESSAGE:
            yield char

    # 返回流式格式的AI信息
    def generateAIMessage(self, payload):
        assistantReply = ''

        try:
            MongoDBConfig.messageManager.addMessage(
                chatId=self.currentChatId,
                messageType="text",
                content=self.userMessage,
                sender="user"
            )
            
            # 发起AI请求
            with requests.post(GlobalState.URL, json=payload, headers=self.HEADERS, stream=True) as response:
                response.raise_for_status()

                response.encoding = 'utf-8'

                for line in response.iter_lines(decode_unicode=True):
                    if (not line or not line.startswith("data: ")): continue

                    data = line[len("data: "):].strip()

                    if (data == "[DONE]"): break

                    try:
                        jsonData = json.loads(data)
                        content = jsonData.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        assistantReply += content

                        if (content):
                            yield content
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"Failed to parse JSON: { line }, Error: { str(e) }")

            # 保存助手消息
            if (assistantReply):
                MongoDBConfig.messageManager.addMessage(
                    chatId=self.currentChatId,
                    messageType="text",
                    content=assistantReply,
                    sender="assistant"
                )

            self.updateContextAndTitle(assistantReply)
        except Exception as e:
            logging.error(f"聊天处理错误: { str(e) }")
            yield f"data: Error: { str(e) }\n\n"
            yield "data: [DONE]\n\n"

    # 更新上下文和标题
    def updateContextAndTitle(self, assistantReply):

        # 更新上下文
        if (self.userId not in self.userContext):
            self.userContext[self.userId] = []

        self.userContext[self.userId].extend([
            {
                "role": "user", 
                "content": self.userMessage
            },
            {
                "role": "assistant", 
                "content": assistantReply
            }
        ])

        if (len(self.userContext[self.userId]) > 10):
            self.userContext[self.userId] = self.userContext[self.userId][-10:]
            
        # 更新标题
        try:
            newTitle = self.userMessage[:20] + "..." if (len(self.userMessage) > 20) else self.userMessage
            MongoDBConfig.chatManager.updateChatTitle(self.currentChatId, newTitle)
        except Exception as e:
            logging.error(f"更新对话标题失败: { str(e) }")

    # 生成AI提示消息
    def generateAIPayload(self):
        messages = [
            {
                "content": self.systemContent,
                "role": "system"
            }
        ] + self.userContext[self.userId] + [
            {"content": self.userMessage, "role": "user"}
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

        return payload