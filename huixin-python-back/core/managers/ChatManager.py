import datetime, logging

from datetime import timezone, datetime
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from bson import ObjectId

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig
    from core.managers.UserManager import UserManager

class ChatManager:
    class Updater:
        def __init__(self, db: "MongoDBConfig.MongoDB"):
            self.db = db

        # 更新对话标题
        def title(self, chatId: str, title: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(chatId)
                }
                updateQuery = {
                    "$set": {
                        "title": title,
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.chats.update_one(idFilter, updateQuery)
                
                return result.modified_count > 0
            except Exception as e:
                logging.error(f"更新对话标题失败: { str(e) }")
                return False
            
        # 更新危险状态
        def danger(self, chatId: str, userId: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(chatId),
                    "userId": ObjectId(userId)
                }
                updateQuery = {
                    "$set": {
                        "type": "dangerous"
                    }
                }

                result = self.db.chats.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"更新危险状态失败: { str(e) }")
                return False

        # 更新管理员
        def admin(self, chatId: str, adminId: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(chatId)
                }
                updateQuery = {
                    "$set": {
                        "adminId": ObjectId(adminId)
                    }
                }

                result = self.db.chats.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"更新管理员失败: { str(e) }")
                return False

        # 隐藏对话
        def hide(self, chatId: str, userId: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(chatId),
                    "userId": ObjectId(userId)
                }
                updateQuery = {
                    "$set": {
                        "isActive": False,
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.chats.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"删除对话失败: { str(e) }")
                return False
            
    class Formatter:
        def doc(self, chat: Dict) -> Dict:
            if (chat):
                chat["_id"] = str(chat["_id"])
                chat["userId"] = str(chat["userId"])
                chat["adminId"] = str(chat["adminId"]) if (chat.get("adminId")) else None

            return chat

        def list(self, chats:List[Dict]) -> List[Dict]:
            return [self.doc(chat) for chat in chats]

    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db
        self.updater = self.Updater(db)
        self.formatter = self.Formatter()

    # 创建新对话, 返回对话ID
    # chatType: "normal" 普通对话, "dangerous" 危险对话
    def createChat(self, userId: str, title: str = "新对话", chatType: str = "normal") -> str:
        chatData = {
            
            # 核心关系与索引字段
            "userId": ObjectId(userId),
            "adminId": None,
            "isActive": True,

            # 核心内容与分类字段
            "title": title,
            "type": chatType,
            "tags": [],  # 可以用于分类对话
            "lastMessage": "",

            # 时间戳
            "timeNode": {
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc),
                "lastMessageAt": None
            },

            # 统计与分析数据
            "stats": {
                "emotionAnalysis": [],  # 情感分析结果
                "dangerLevel": 0,  # 危险等级
                "messageCount": 0,  # 消息数量
            }
        }
        
        result = self.db.chats.insert_one(chatData)
        chatId = str(result.inserted_id)
        
        # 更新用户统计
        UserManager(self.db).updater.stats(userId, chats=1)

        return chatId

    # 获取用户的对话列表
    def getUserChats(self, userId: str, page: int = 1, limit: int = 20) -> Tuple[List[Dict], int]:
        try:
            idFilter = {
                "userId": ObjectId(userId),
                "isActive": True
            }
            projection = {
                "_id": 1,
                "userId": 1,
                "title": 1,
                "lastMessage": 1,
                "timeNode.updatedAt": 1,
                "type": 1
            }
            sort = [("timeNode.updatedAt", -1)]
            skip = (page - 1) * limit
            total = self.db.chats.count_documents(idFilter)
            chats = list(self.db.chats.find(idFilter, projection)
                .sort(sort)
                .skip(skip)
                .limit(limit))

            return (self.formatter.list(chats), total)
        except Exception as e:
            logging.error(f"❌ 获取对话列表失败: { str(e) }")
            return ([], 0)

    # 根据ID获取对话
    def getChatById(self, chatId: str) -> Optional[Dict]:
        try:
            idFilter = {
                "_id": ObjectId(chatId),
                "isActive": True
            }
            chat = self.db.chats.find_one(idFilter)

            return self.formatter.doc(chat) if (chat) else None
        except Exception as e:
            logging.error(f"❌ 获取对话失败: { str(e) }")
            return None

    # 获取所有未被分配的危险对话列表
    def getUnsignedDangerousChats(self, limit: int = 50) -> Tuple[List[Dict], int]:
        try:
            idFilter = {
                "type": "dangerous",
                "adminId": None,
                "isActive": True
            }
            sort = [("timeNode.updatedAt", -1)]
            total = self.db.chats.count_documents(idFilter)
            chats = list(self.db.chats.find(idFilter)
                .sort(sort)
                .limit(limit))

            return (self.formatter.list(chats), total)
        except Exception as e:
            logging.error(f"❌ 获取未分配的危险对话失败: { str(e) }")
            return ([], 0)
