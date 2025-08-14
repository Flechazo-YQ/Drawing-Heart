import datetime, logging

from datetime import datetime, timezone
from typing import List, Dict, Optional, TYPE_CHECKING
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
                        "state.isEdited": True,
                        "state.editedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.messages.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"更新消息失败: {str(e)}")
                return False

        def hide(self, messageId: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(messageId)
                }
                updateQuery = {
                    "$set": {
                        "state.isVisible": False
                    }
                }
                result = self.db.messages.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"隐藏消息失败: {str(e)}")
                return False

    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db
        self.updater = self.Updater(db)

    # 添加消息到对话的messages数组中
    # type: text, image, drawing, system
    # sender: user, assistant, system
    def createMessage(self, chatId: str, type: str, content: str, sender: str = "user", **kwargs) -> str | None:
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
        
        try:
            result = self.db.messages.insert_one(messageData)
            idFilter = {
                "_id": ObjectId(chatId)
            }

            updateQuery = {
                "$set": {
                    "lastMessage": content,
                    "timeNode.updatedAt": messageData["timestamp"],
                    "timeNode.lastMessageAt": messageData["timestamp"]
                },
                "$inc": {
                    "stats.messagesCount": 1
                }
            }

            self.db.chats.update_one(idFilter, updateQuery)
            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"添加消息失败: { str(e) }")
            return None
    
    # 获取对话的消息列表
    def getMessagesList(self, chatId: str, page: int = 1, limit: int = 50) -> List[Dict]:
        try:
            skipCount = (page - 1) * limit
            idFilter = {
                "chatId": ObjectId(chatId),
                "state.isVisible": True  # 使用新的数据结构
            }
            messages = list(
                self.db.messages.find(idFilter)
                    .sort("timestamp", 1)
                    .skip(skipCount)
                    .limit(limit)
            )

            return messages
        except Exception as e:
            logging.error(f"获取消息列表失败: { str(e) }")
            return []

    # 获取最新的几条消息(用于上下文)
    def getLatestMessages(self, chatId: str, count: int = 10) -> List[Dict]:
        try:
            idFilter = {
                "chatId": ObjectId(chatId),
                "state.isVisible": True
            }
            messages = list(
                self.db.messages.find(idFilter)
                    .sort("timestamp", -1)
                    .limit(count)
            )

            return messages[::-1]
        except Exception as e:
            logging.error(f"获取最新消息失败: { str(e) }")
            return []

    # 获取完整的对话数据(包含所有消息)
    def getAllMessages(self, chatId: str) -> Optional[Dict]:
        try:
            chatIdFilter = {
                "_id": ObjectId(chatId)
            }
            pipeline = [
                { 
                    "$match": chatIdFilter
                },
                
                # 使用 $lookup 连接 messages 集合
                {
                    "$lookup": {
                        "from": "messages",
                        "localField": "_id",
                        "foreignField": "chatId",
                        "as": "messages" # 动态创建 messages 字段
                    }
                },

                # 在数据库层面处理 messages 数组
                {
                    "$addFields": {
                        "messages": {
                            "$filter": { # 过滤数组
                                "input": "$messages",
                                "as": "msg",
                                "cond": { "$eq": [ "$$msg.state.isVisible", True ] }
                            }
                        }
                    }
                },

                # 在数据库层面排序 messages 数组
                {
                    "$addFields": {
                        "messages": {
                            "$sortArray": { # 对数组内元素排序 (MongoDB 5.2+)
                                "input": "$messages",
                                "sortBy": { "timestamp": 1 }
                            }
                        }
                    }
                }
            ]
            result = list(self.db.chats.aggregate(pipeline))

            if (not result): 
                return None

            return result[0]
        except Exception as e:
            logging.error(f"获取完整对话失败: { str(e) }")
            return None