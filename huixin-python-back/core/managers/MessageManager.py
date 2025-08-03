import datetime, logging, uuid

from core.configs.MongoDBConfig import MongoDBConfig

from typing import List, Dict, Optional
from bson import ObjectId

class MessageManager:

    def __init__(self, db: MongoDBConfig.MongoDB):
        self.db = db

    # 添加消息到对话的messages数组中
    # messageType: text, image, drawing, system
    # sender: user, assistant, system
    def addMessage(self, chatId: str, messageType: str, content: str, sender: str = "user", **kwargs) -> str | None:
        messageId = str(uuid.uuid4())  # 生成唯一消息ID
        messageData = {
            "_id": messageId,
            "message_type": messageType,
            "content": content,
            "sender": sender,
            "timestamp": datetime.datetime.utcnow(),
            "metadata": {
                "emotion_score": kwargs.get("emotion_score"),
                "danger_level": kwargs.get("danger_level", 0),
                "image_url": kwargs.get("image_url"),
                "drawing_data": kwargs.get("drawing_data"),
                "processing_time": kwargs.get("processing_time"),
                "model_version": kwargs.get("model_version"),
                "tokens_used": kwargs.get("tokens_used")
            },
            "is_visible": True,
            "edited_at": None,
            "reply_to": kwargs.get("reply_to")  # 回复消息ID
        }
        
        try:
            # 将消息添加到对话的messages数组中
            result = self.db.chats.update_one(
                {"_id": ObjectId(chatId)},
                {
                    "$push": { "messages": messageData },
                    "$inc": { "message_count": 1 },
                    "$set": {
                        "last_message_at": datetime.datetime.utcnow(),
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            
            if (result.modified_count <= 0):
                logging.error(f"添加消息失败，对话ID不存在: { chatId }")
                return None
            
            return messageId
        except Exception as e:
            logging.error(f"添加消息失败: { str(e) }")
            return None
    
    # 获取对话的消息列表
    def getChatMessages(self, chatId: str, page: int = 1, limit: int = 50) -> List[Dict]:
        try:
            # 从对话文档中获取messages数组
            chat = self.db.chats.find_one(
                { "_id": ObjectId(chatId), "is_active": True },
                { "messages": 1 }
            )
            
            if (not chat):
                return []
            
            messages = chat.get("messages", [])
            
            # 过滤可见消息
            visibleMessages = [msg for msg in messages if (msg.get("is_visible", True))]
            
            # 分页处理
            startIndex = (page - 1) * limit
            endIndex = startIndex + limit
            paginatedMessages = visibleMessages[startIndex : endIndex]

            return paginatedMessages
        except Exception as e:
            logging.error(f"获取消息列表失败: { str(e) }")
            return []

    # 获取最新的几条消息(用于上下文)
    def getLatestMessages(self, chatId: str, count: int = 10) -> List[Dict]:
        try:
            # 从对话文档中获取messages数组
            chat = self.db.chats.find_one(
                { "_id": ObjectId(chatId), "is_active": True },
                { "messages": 1 }
            )
            
            if (not chat):
                return []
            
            messages = chat.get("messages", [])
            
            # 过滤可见消息并取最新的几条
            visibleMessages = [msg for msg in messages if (msg.get("is_visible", True))]
            latestMessages = visibleMessages[-count:] if (len(visibleMessages) > count) else visibleMessages

            return latestMessages
        except Exception as e:
            logging.error(f"获取最新消息失败: { str(e) }")
            return []

    # 隐藏消息(软删除)
    def hideMessage(self, chatId: str, messageId: str) -> bool:
        try:
            result = self.db.chats.update_one(
                {
                    "_id": ObjectId(chatId),
                    "messages._id": messageId
                },
                {
                    "$set": {
                        "messages.$.is_visible": False
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"隐藏消息失败: {str(e)}")
            return False
    
    # 更新消息内容
    def updateMessage(self, chatId: str, messageId: str, content: str) -> bool:
        try:
            result = self.db.chats.update_one(
                {
                    "_id": ObjectId(chatId),
                    "messages._id": messageId
                },
                {
                    "$set": {
                        "messages.$.content": content,
                        "messages.$.edited_at": datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新消息失败: {str(e)}")
            return False

    # 获取完整的对话数据(包含所有消息)
    def getChatWithMessages(self, chatId: str) -> Optional[Dict]:
        try:
            chat = self.db.chats.find_one({
                "_id": ObjectId(chatId), 
                "is_active": True
            })

            if (chat):
                chat["_id"] = str(chat["_id"])
                chat["user_id"] = str(chat["user_id"])
                
                # 过滤可见消息
                if ("messages" in chat):
                    chat["messages"] = [msg for msg in chat["messages"] if (msg.get("is_visible", True))]

            return chat
        except Exception as e:
            logging.error(f"获取完整对话失败: { str(e) }")
            return None