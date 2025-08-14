import flask, requests, json, logging, datetime

from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.states.GlobalState import GlobalState

from flask import Response
from typing import Final, List, Dict

class StreamChatHandler:
    DANGER_KEYWORDS: Final[list[str]] = ["自杀", "自残", "死", "想死", "活不下去", "结束生命", "轻生"]
    ADMIN_MESSAGE: Final[str] = "系统检测到您的内容可能存在风险, 已切换到人工客服模式。请稍等片刻, 管理员正在审核您的对话..."
    HEADERS: Final[dict[str, str]] = {
        "Authorization": "Bearer sk-bhgbmuxblqtroypztkuonssqqkitngencupdofitajnmvbtv",
        "Content-Type": "application/json"
    }

    def __init__(self, userId: str, chatId: str, userMessage: str):
        self.userId = userId
        self.chatId = chatId
        self.userMessage = userMessage

        self.user = MongoDBConfig.userManager.getUserById(self.userId)
        self.userName = self.user.get("name", "未知用户") if (self.user) else "未知用户"
        self.dangerLevel = self.__processStreamDanger(userMessage)
        self.systemContent = ""

    # 处理流程的主入口
    def processStream(self):
        return self.__handleDangerousMessage() if (self.dangerLevel > 0.3) else self.__handleNormalMessage()

    # 分析消息危险等级
    def __processStreamDanger(self, message: str):
        try:
            if (any(keyword in message for keyword in self.DANGER_KEYWORDS)):
                logging.warning(f"⚠️ 检测到危险关键词: { message }")
                return 0.9
            
            (label, probs) = GlobalState.CLASSIFIER.predict(message) if (GlobalState.CLASSIFIER) else (None, None)
            dangerProb = float(probs[0]) if (probs) else 0.0

            logging.info(f"危险检测结果: label={ label }, dangerous_prob={ dangerProb:.4f }")
            return dangerProb
        except Exception as e:
            logging.error(f"❌ 情感分析模型预测失败: { str(e) }")
            return 0.9 if (any(keyword in message for keyword in self.DANGER_KEYWORDS)) else 0.0

    # 处理危险消息
    def __handleDangerousMessage(self):
        logging.warning(f"⚠️ 触发危险检测: dangerous={ self.dangerLevel:.4f } > 0.3")
        MongoDBConfig.chatManager.updater.danger(self.chatId, self.userId)
        MongoDBConfig.messageManager.createMessage(
            chatId=self.chatId,
            type="text",
            content=self.userMessage,
            sender="user",
            dangerLevel=self.dangerLevel
        )

        alertData = {
            "chatId": self.chatId,
            "userId": self.userId,
            "userName": self.userName,
            "message": self.userMessage,
            "dangerLevel": self.dangerLevel
        }

        SocketQueueHandler.queueEmit("dangerous_chat_alert", alertData, "admin_room")
        logging.info(f"✅ 已发送危险对话通知到管理员房间 (ChatID: { self.chatId })")

        MongoDBConfig.messageManager.createMessage(
            chatId=self.chatId,
            type="text",
            content=self.ADMIN_MESSAGE,
            sender="system"
        )

        def generateStream():
            for char in self.ADMIN_MESSAGE:
                yield f"data: { json.dumps({ 'content': char }) }\n\n"

            yield "data: [DONE]\n\n"

        return Response(
            flask.stream_with_context(generateStream()),
            mimetype="text/event-stream"
        )

    # 处理正常消息
    def __handleNormalMessage(self):
        self.__prepareSystemContent()

        context = MongoDBConfig.messageManager.getLatestMessages(self.chatId)
        payload = self.__generateAIPayload(context)

        return Response(
            flask.stream_with_context(self.__generateAIMessage(payload)),
            mimetype="text/event-stream"
        )

    # 准备AI需要的系统提示词
    def __prepareSystemContent(self):
        try:
            latestAnalysis = MongoDBConfig.drawingManager.getRecentAnalysis(self.userId, hours=4)

            if (not latestAnalysis):
                self.systemContent = "你现在是一名心理医师, 你的名字叫绘心同学。\
                    请用温暖、专业的语言与用户交流, 用多轮对话的形式, 每次别说太多。\
                    如果用户需要心理绘画分析, 请引导他们先完成绘画测试。"
            else:
                analysisDate = latestAnalysis["timeNode"]["createdAt"].strftime("%Y-%m-%d")
                analysisResult = latestAnalysis["analysis"]["resultText"]
                self.systemContent = f"你现在是一名心理医师, 你的名字叫绘心同学。\
                    用户在{ analysisDate }完成了心理绘画测试, 以下是最新的分析结果：{ analysisResult } \n\n\
                    请结合这个分析结果帮助用户, 用通俗易懂的语言与用户交流, 用多轮对话的形式, 每次别说太多。\
                    如果用户的问题与绘画分析相关, 请参考分析结果给出建议。"
        except Exception as e:
            logging.error(f"❌ 准备系统内容失败: { str(e) }")
            self.systemContent = "你现在是一名心理医师, 你的名字叫绘心同学。\
                请用温暖、专业的语言与用户交流, 用多轮对话的形式, 每次别说太多。\
                如果用户需要心理绘画分析, 请引导他们先完成绘画测试。"

    # 返回流式格式的AI信息
    def __generateAIMessage(self, payload):
        assistantReply = ""

        try:
            MongoDBConfig.messageManager.createMessage(
                chatId=self.chatId,
                type="text",
                content=self.userMessage,
                sender="user"
            )
            
            # 发起AI请求
            with requests.post(GlobalState.URL, json=payload, headers=self.HEADERS, stream=True) as response:
                response.raise_for_status()

                response.encoding = "utf-8"

                for line in response.iter_lines(decode_unicode=True):
                    if (not line or not line.startswith("data: ")): continue

                    data = line[len("data: "):].strip()

                    if (data == "[DONE]"): break

                    try:
                        content = json.loads(data).get("choices", [{}])[0].get("delta", {}).get("content", "")
                        assistantReply += content

                        if (content): yield content
                    except (json.JSONDecodeError, Exception) as e:
                        logging.error(f"❌ Failed to parse JSON: { line }, Error: { str(e) }")

            # 保存助手消息
            if (assistantReply):
                MongoDBConfig.messageManager.createMessage(
                    chatId=self.chatId,
                    type="text",
                    content=assistantReply,
                    sender="assistant"
                )
        except Exception as e:
            logging.error(f"聊天处理错误: { str(e) }")
            yield f"data: Error: { str(e) }\n\n"
            yield "data: [DONE]\n\n"

    # 生成AI提示消息
    def __generateAIPayload(self, context: List[Dict]):
        formattedContext = [{ "role": msg["sender"], "content": msg["content"] } for msg in context]
        messages = [{
            "role": "system", 
            "content": self.systemContent
        }] + formattedContext + [{
            "role": "user", 
            "content": self.userMessage
        }]

        return {
            "model": "Pro/deepseek-ai/DeepSeek-V3",
            "stream": True,
            "max_tokens": 512,
            "temperature": 0.7,
            "messages": messages
        }
