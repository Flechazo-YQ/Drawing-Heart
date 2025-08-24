import datetime, logging

from core.utils.FormatHelper import FormatHelper

from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from bson import ObjectId

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class MessageManager:
    class Updater:
        def __init__(self, db: "MongoDBConfig.MongoDB"):
            self.db = db

        def content(self, messageId: str, content: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(messageId)
                }
                updateQuery = {
                    "$set": {
                        "content": content,
                        "stats.isEdited": True,
                        "stats.editedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.messages.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 更新消息失败: {str(e)}")
                return False

        def hide(self, messageId: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(messageId)
                }
                updateQuery = {
                    "$set": {
                        "stats.isVisible": False
                    }
                }
                result = self.db.messages.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 隐藏消息失败: {str(e)}")
                return False

    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db
        self.updater = self.Updater(db)

    # 添加消息到对话
    # type: text, image, drawing, system
    # sender: user, assistant, system
    def createMessage(self, chatId: str, type: str, content: str, sender: str = "user", **kwargs):
        try:
            idFilter = {
                "_id": ObjectId(chatId)
            }
            chat = self.db.chats.find_one(idFilter)

            if (not chat):
                logging.error(f"❌ 对话不存在: { chatId }")
    
                return None
            
            messageData = {
                
                # 核心索引与关系字段
                "chatId": chatId,
                "timestamp": datetime.now(timezone.utc),

                # 核心内容字段
                "sender": sender,
                "type": type,
                "content": content,

                # 状态信息
                "stats": {
                    "isVisible": True,
                    "isEdited": False,
                    "editedAt": None,
                    "readBy": []
                },

                # 关系信息
                "relations": {
                    "replyTo": kwargs.get("replyTo")
                },

                # 元数据
                "metaData": {
                    "emotionScore": kwargs.get("emotionScore"),
                    "dangerLevel": kwargs.get("dangerLevel", 0),
                    "imageUrl": kwargs.get("imageUrl"),
                    "drawingData": kwargs.get("drawingData"),
                    "processingTime": kwargs.get("processingTime"),
                    "modelVersion": kwargs.get("modelVersion"),
                    "tokensUsed": kwargs.get("tokensUsed")
                }
            }

            self.db.messages.insert_one(messageData)
            
            updateQuery = {
                "$set": {
                    "lastMessage": content,
                    "timeNode.updatedAt": messageData["timestamp"],
                    "timeNode.lastMessageAt": messageData["timestamp"]
                },
                "$inc": {
                    "stats.messageCount": 1
                }
            }

            self.db.chats.update_one(idFilter, updateQuery)

            return FormatHelper.jsonOrList(messageData)
        except Exception as e:
            logging.error(f"❌ 添加消息失败: { str(e) }")
            return None
    
    # 获取对话的消息列表
    def getMessagesList(self, chatId: str, page: int = 1, limit: int = 50) -> List[Dict]:
        try:
            skipCount = (page - 1) * limit
            idFilter = {
                "chatId": chatId,
                "stats.isVisible": True
            }
            messages = list(self.db.messages.find(idFilter)
                .sort("timestamp", 1)
                .skip(skipCount)
                .limit(limit))

            return FormatHelper.jsonOrList(messages)
        except Exception as e:
            logging.error(f"❌ 获取消息列表失败: { str(e) }")
            return []

    # 获取最新的几条消息(用于上下文)
    def getLatestMessages(self, chatId: str, count: int = 10) -> List[Dict]:
        try:
            idFilter = {
                "chatId": chatId,
                "stats.isVisible": True
            }
            messages = list(self.db.messages.find(idFilter)
                .sort("timestamp", -1)
                .limit(count))

            return FormatHelper.jsonOrList(messages)[::-1]
        except Exception as e:
            logging.error(f"❌ 获取最新消息失败: { str(e) }")
            return []
        

        