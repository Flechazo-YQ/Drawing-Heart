import datetime, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.TokenState import TokenState

from typing import Dict, Optional
from bson import ObjectId

class UserManager:

    def __init__(self, db: MongoDBConfig.MongoDB):
        self.db = db
        
    # 创建新用户, 返回用户ID
    def createUser(self, username: str, password: str, email: str, gender: str, **kwargs) -> str:
        
        # 密码哈希处理
        hashedPassword = TokenState.sha256Hash(password)
        userData = {
            "username": username,
            "email": email,
            "password": hashedPassword,  # 存储哈希后的密码
            "chance": kwargs.get("chance", 10),  # 默认机会次数
            "is_team": kwargs.get("is_team", ""),
            "avatar": kwargs.get("avatar", ""),
            "gender": gender,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "is_active": True,
            "total_chats": 0,
            "total_messages": 0
        }
        result = self.db.users.insert_one(userData)

        return str(result.inserted_id)
        
    # 验证用户密码
    def verifyPassword(self, username: str, password: str) -> bool:        
        user = self.getUserByUsername(username)

        if (not user):
            return False
            
        # 哈希输入的密码并与存储的哈希值比较
        hashedPassword = TokenState.sha256Hash(password)

        return user.get('password') == hashedPassword
    
    # 直接验证密码与存储的哈希值是否匹配
    def verifyPasswordByHash(self, password: str, storedHash: str) -> bool:
        
        # 哈希输入的密码并与存储的哈希值比较
        hashedPassword = TokenState.sha256Hash(password)

        return storedHash == hashedPassword

    # 根据邮箱获取用户
    def getUserByEmail(self, email: str) -> Optional[Dict]:
        return self.db.users.find_one({
            "email": email, 
            "is_active": True
        })
    
    # 根据用户名获取用户
    def getUserByUsername(self, username: str) -> Optional[Dict]:
        return self.db.users.find_one({
            "username": username, 
            "is_active": True
        })

    # 根据ID获取用户
    def getUserById(self, userId: str) -> Optional[Dict]:
        try:
            # 验证userId是否为有效的ObjectId字符串
            if (not ObjectId.is_valid(userId)):
                logging.warning(f"提供的userId不是有效的ObjectId: { userId }")
                return None

            return self.db.users.find_one({
                "_id": ObjectId(userId), 
                "is_active": True
            })
        except Exception as e:
            logging.error(f"根据ID获取用户时发生错误 (userId: { userId }): { str(e) }")

            return None

    # 根据ID更新用户密码
    def updatePasswordById(self, userId: str, newPassword: str) -> bool:
        try:
            # 哈希新密码
            hashedPassword = TokenState.sha256Hash(newPassword)
            result = self.db.users.update_one(
                { "_id": ObjectId(userId) },
                {
                    "$set": {
                        "password": hashedPassword,
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )

            logging.info(f"更新用户密码成功: userId={ userId }")
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新用户密码失败: { str(e) }")
            return False

    # 更新用户信息
    def updateUser(self, userId: str, updateData: Dict) -> bool:
        try:
            updateData["updated_at"] = datetime.datetime.utcnow()
            result = self.db.users.update_one(
                { "_id": ObjectId(userId) },
                { "$set": updateData }
            )
            return result.modified_count > 0
        except:
            return False

    # 增加用户统计数据
    def incrementUserStats(self, userId: str, chats: int = 0, messages: int = 0):
        try:
            incData = {}

            if (chats > 0):
                incData["total_chats"] = chats

            if (messages > 0):
                incData["total_messages"] = messages

            updateData = {"updated_at": datetime.datetime.utcnow()}
            updateQuery = {}

            if (incData):
                updateQuery["$inc"] = incData

            updateQuery["$set"] = updateData

            self.db.users.update_one(
                {"_id": ObjectId(userId)},
                updateQuery
            )
        except Exception as e:
            logging.error(f"更新用户统计失败: { str(e) }")