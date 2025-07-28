from pymongo import MongoClient
from bson import ObjectId
import datetime
from typing import Optional, Dict, List
import logging

class MongoDB:
    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="huixin_db"):
        """
        初始化MongoDB连接
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            # 测试连接
            self.client.server_info()
            logging.info(f"成功连接到MongoDB数据库: {database_name}")
        except Exception as e:
            logging.error(f"连接MongoDB失败: {str(e)}")
            raise e
        
        # 获取集合
        self.users = self.db.users
        self.chats = self.db.chats
        self.messages = self.db.messages
        
        # 创建索引
        self._create_indexes()
    
    def _create_indexes(self):
        """创建数据库索引优化查询性能"""
        try:
            # 用户集合索引
            self.users.create_index("email", unique=True)
            self.users.create_index("username")
            
            # 对话集合索引
            self.chats.create_index("user_id")
            self.chats.create_index("created_at")
            self.chats.create_index([("user_id", 1), ("created_at", -1)])
            # 为消息数组中的字段创建索引
            self.chats.create_index("messages.timestamp")
            self.chats.create_index("messages.sender")
            
            logging.info("数据库索引创建完成")
        except Exception as e:
            logging.warning(f"创建索引时出现警告: {str(e)}")

class UserManager:
    def __init__(self, db: MongoDB):
        self.db = db
        
    def create_user(self, username: str, email: str, password: str, **kwargs) -> str:
        """
        创建新用户
        返回用户ID
        """
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "chance": kwargs.get("chance", 10),  # 默认机会次数
            "is_team": kwargs.get("is_team", ""),
            "avatar": kwargs.get("avatar", ""),
            "gender": kwargs.get("gender", ""),
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "is_active": True,
            "total_chats": 0,
            "total_messages": 0
        }
        
        result = self.db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        return self.db.users.find_one({"email": email, "is_active": True})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """根据ID获取用户"""
        try:
            return self.db.users.find_one({"_id": ObjectId(user_id), "is_active": True})
        except:
            return None
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """更新用户信息"""
        try:
            update_data["updated_at"] = datetime.datetime.utcnow()
            result = self.db.users.update_one(
                {"_id": ObjectId(user_id)}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def increment_user_stats(self, user_id: str, chats: int = 0, messages: int = 0):
        """增加用户统计数据"""
        try:
            update_data = {"updated_at": datetime.datetime.utcnow()}
            if chats > 0:
                update_data["total_chats"] = chats
            if messages > 0:
                update_data["total_messages"] = messages
                
            self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": update_data}
            )
        except Exception as e:
            logging.error(f"更新用户统计失败: {str(e)}")

class ChatManager:
    def __init__(self, db: MongoDB):
        self.db = db
        
    def create_chat(self, user_id: str, title: str = "新对话", chat_type: str = "normal") -> str:
        """
        创建新对话
        返回对话ID
        chat_type: "normal" 普通对话, "dangerous" 危险对话
        """
        chat_data = {
            "user_id": ObjectId(user_id),
            "title": title,
            "type": chat_type,  # 新增：对话类型字段
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
        
        result = self.db.chats.insert_one(chat_data)
        chat_id = str(result.inserted_id)
        
        # 更新用户统计
        UserManager(self.db).increment_user_stats(user_id, chats=1)
        
        return chat_id
    
    def get_user_chats(self, user_id: str, page: int = 1, limit: int = 20) -> List[Dict]:
        """获取用户的对话列表"""
        try:
            skip = (page - 1) * limit
            chats = list(self.db.chats.find(
                {"user_id": ObjectId(user_id), "is_active": True}
            ).sort("updated_at", -1).skip(skip).limit(limit))
            
            # 转换ObjectId为字符串，并获取每个对话的最后一条消息
            for chat in chats:
                chat["_id"] = str(chat["_id"])
                chat["user_id"] = str(chat["user_id"])
                
                # 从集成的messages数组中获取最后一条用户消息作为显示标题
                messages = chat.get("messages", [])
                last_user_message = None
                
                # 从后往前查找最后一条用户消息（对话结束前的最后一条语言）
                for msg in reversed(messages):
                    if msg.get("sender") == "user" and msg.get("is_visible", True):
                        last_user_message = msg
                        break
                
                # 标题始终使用最后一条用户消息，如果没有则显示对话类型
                if last_user_message:
                    # 截取消息内容作为标题，最多20个字符
                    content = last_user_message.get("content", "")
                    chat["display_title"] = content[:20] + "..." if len(content) > 20 else content
                else:
                    # 根据对话类型显示不同的默认标题
                    chat_type = chat.get("type", "normal")
                    if chat_type == "dangerous":
                        chat["display_title"] = "危险对话"
                    else:
                        chat["display_title"] = "新对话"
                
                # 移除messages数组以减少返回数据量（在列表页面不需要完整消息）
                chat.pop("messages", None)
                
            return chats
        except Exception as e:
            logging.error(f"获取对话列表失败: {str(e)}")
            return []
    
    def get_chat_by_id(self, chat_id: str) -> Optional[Dict]:
        """根据ID获取对话"""
        try:
            chat = self.db.chats.find_one({"_id": ObjectId(chat_id), "is_active": True})
            if chat:
                chat["_id"] = str(chat["_id"])
                chat["user_id"] = str(chat["user_id"])
            return chat
        except:
            return None
    
    def update_chat(self, chat_id: str, update_data: Dict) -> bool:
        """更新对话信息"""
        try:
            update_data["updated_at"] = datetime.datetime.utcnow()
            result = self.db.chats.update_one(
                {"_id": ObjectId(chat_id)}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def hide_chat(self, chat_id: str) -> bool:
        """隐藏对话（软删除）"""
        return self.update_chat(chat_id, {"is_active": False})
    
    def update_chat_title(self, chat_id: str, title: str) -> bool:
        """更新对话标题"""
        try:
            result = self.db.chats.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {
                        "title": title,
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新对话标题失败: {str(e)}")
            return False

class MessageManager:
    def __init__(self, db: MongoDB):
        self.db = db
        
    def add_message(self, chat_id: str, message_type: str, content: str, 
                   sender: str = "user", **kwargs) -> str:
        """
        添加消息到对话的messages数组中
        message_type: text, image, drawing, system
        sender: user, assistant, system
        """
        import uuid
        message_id = str(uuid.uuid4())  # 生成唯一消息ID
        
        message_data = {
            "_id": message_id,
            "message_type": message_type,
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
                {"_id": ObjectId(chat_id)},
                {
                    "$push": {"messages": message_data},
                    "$inc": {"message_count": 1},
                    "$set": {
                        "last_message_at": datetime.datetime.utcnow(),
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return message_id
            else:
                logging.error(f"添加消息失败，对话ID不存在: {chat_id}")
                return None
                
        except Exception as e:
            logging.error(f"添加消息失败: {str(e)}")
            return None
    
    def get_chat_messages(self, chat_id: str, page: int = 1, limit: int = 50) -> List[Dict]:
        """获取对话的消息列表"""
        try:
            # 从对话文档中获取messages数组
            chat = self.db.chats.find_one(
                {"_id": ObjectId(chat_id), "is_active": True},
                {"messages": 1}
            )
            
            if not chat:
                return []
            
            messages = chat.get("messages", [])
            
            # 过滤可见消息
            visible_messages = [msg for msg in messages if msg.get("is_visible", True)]
            
            # 分页处理
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_messages = visible_messages[start_idx:end_idx]
            
            return paginated_messages
        except Exception as e:
            logging.error(f"获取消息列表失败: {str(e)}")
            return []
    
    def get_latest_messages(self, chat_id: str, count: int = 10) -> List[Dict]:
        """获取最新的几条消息（用于上下文）"""
        try:
            # 从对话文档中获取messages数组
            chat = self.db.chats.find_one(
                {"_id": ObjectId(chat_id), "is_active": True},
                {"messages": 1}
            )
            
            if not chat:
                return []
            
            messages = chat.get("messages", [])
            
            # 过滤可见消息并取最新的几条
            visible_messages = [msg for msg in messages if msg.get("is_visible", True)]
            latest_messages = visible_messages[-count:] if len(visible_messages) > count else visible_messages
            
            return latest_messages
        except Exception as e:
            logging.error(f"获取最新消息失败: {str(e)}")
            return []
    
    def hide_message(self, chat_id: str, message_id: str) -> bool:
        """隐藏消息（软删除）"""
        try:
            result = self.db.chats.update_one(
                {
                    "_id": ObjectId(chat_id),
                    "messages._id": message_id
                },
                {"$set": {"messages.$.is_visible": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"隐藏消息失败: {str(e)}")
            return False
    
    def update_message(self, chat_id: str, message_id: str, content: str) -> bool:
        """更新消息内容"""
        try:
            result = self.db.chats.update_one(
                {
                    "_id": ObjectId(chat_id),
                    "messages._id": message_id
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
    
    def get_chat_with_messages(self, chat_id: str) -> Optional[Dict]:
        """获取完整的对话数据（包含所有消息）"""
        try:
            chat = self.db.chats.find_one({"_id": ObjectId(chat_id), "is_active": True})
            if chat:
                chat["_id"] = str(chat["_id"])
                chat["user_id"] = str(chat["user_id"])
                
                # 过滤可见消息
                if "messages" in chat:
                    chat["messages"] = [msg for msg in chat["messages"] if msg.get("is_visible", True)]
                
            return chat
        except Exception as e:
            logging.error(f"获取完整对话失败: {str(e)}")
            return None

# 全局数据库实例
mongodb = None
user_manager = None
chat_manager = None
message_manager = None

def init_mongodb(connection_string="mongodb://localhost:27017/", database_name="huixin_db"):
    """初始化MongoDB连接"""
    global mongodb, user_manager, chat_manager, message_manager
    
    mongodb = MongoDB(connection_string, database_name)
    user_manager = UserManager(mongodb)
    chat_manager = ChatManager(mongodb)
    message_manager = MessageManager(mongodb)
    
    logging.info("MongoDB初始化完成")
    return mongodb
