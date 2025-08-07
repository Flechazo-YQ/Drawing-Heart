import datetime, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.managers.UserManager import UserManager

from typing import List, Dict, Optional
from bson import ObjectId

class ChatManager:
    
    def __init__(self, db: MongoDBConfig.MongoDB):
        self.db = db
        
    # 创建新对话, 返回对话ID
    # chat_type: "normal" 普通对话, "dangerous" 危险对话
    def createChat(self, userId: str, title: str = "新对话", chatType: str = "normal") -> str:
        chatData = {
            "user_id": ObjectId(userId),
            "title": title,
            "type": chatType,  # 新增：对话类型字段
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "is_active": True,
            "message_count": 0,
            "last_message_at": None,
            "messages": [],  # 直接在对话中存储所有消息
            "tags": [],  # 可以用于分类对话
            "metadata": {
                "emotion_analysis": [],  # 情感分析结果
                "danger_level": 0,  # 危险等级
                "image_count": 0,  # 图片数量
                "drawing_count": 0  # 绘画数量
            }
        }
        
        result = self.db.chats.insert_one(chatData)
        chatId = str(result.inserted_id)
        
        # 更新用户统计
        UserManager(self.db).incrementUserStats(userId, chats=1)

        return chatId

    # 获取用户的对话列表
    def getUserChats(self, userId: str, page: int = 1, limit: int = 20) -> List[Dict]:
        try:
            skip = (page - 1) * limit
            chats = list(self.db.chats.find({
                "user_id": ObjectId(userId), 
                "is_active": True
            })
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit))
            
            # 转换ObjectId为字符串，并获取每个对话的最后一条消息
            for chat in chats:
                chat["_id"] = str(chat["_id"])
                chat["user_id"] = str(chat["user_id"])
                
                # 从集成的messages数组中获取最后一条用户消息作为显示标题
                messages = chat.get("messages", [])
                lastUserMessage = None
                
                # 从后往前查找最后一条用户消息（对话结束前的最后一条语言）
                for msg in reversed(messages):
                    if (msg.get("sender") == "user" and msg.get("is_visible", True)):
                        lastUserMessage = msg
                        break
                
                # 标题始终使用最后一条用户消息，如果没有则显示对话类型
                if (lastUserMessage):
                    # 截取消息内容作为标题，最多20个字符
                    content = lastUserMessage.get("content", "")
                    chat["display_title"] = content[:20] + "..." if (len(content) > 20) else content
                else:
                    # 根据对话类型显示不同的默认标题
                    chatType = chat.get("type", "normal")
                    chat["display_title"] = "危险对话" if (chatType == "dangerous") else "新对话"
                
                # 移除messages数组以减少返回数据量（在列表页面不需要完整消息）
                chat.pop("messages", None)
                
            return chats
        except Exception as e:
            logging.error(f"获取对话列表失败: { str(e) }")
            return []
    
    # 根据ID获取对话
    def getChatById(self, chatId: str) -> Optional[Dict]:
        try:
            chat = self.db.chats.find_one({
                "_id": ObjectId(chatId), 
                "is_active": True
            })

            if (chat):
                chat["_id"] = str(chat["_id"])
                chat["user_id"] = str(chat["user_id"])
            return chat
        except:
            return None

    # 更新对话信息
    def updateChat(self, chatId: str, updateData: Dict) -> bool:
        try:
            updateData["updated_at"] = datetime.datetime.utcnow()
            result = self.db.chats.update_one(
                { "_id": ObjectId(chatId) },
                { "$set": updateData }
            )
            return result.modified_count > 0
        except:
            return False

    # 隐藏对话（软删除）
    def hideChat(self, chatId: str) -> bool:
        return self.updateChat(chatId, { "is_active": False })

    # 删除对话（硬删除）
    def deleteChat(self, chatId: str, userId: str) -> bool:
        try:
            result = self.db.chats.delete_one({
                "_id": ObjectId(chatId),
                "user_id": ObjectId(userId)
            })

            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"删除对话失败: { str(e) }")
            return False

    # 更新对话标题
    def updateChatTitle(self, chatId: str, title: str) -> bool:
        try:
            result = self.db.chats.update_one(
                {"_id": ObjectId(chatId)},
                {
                    "$set": {
                        "title": title,
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新对话标题失败: { str(e) }")
            return False