import datetime, logging

from core.utils.PasswordHelper import PasswordHelper

from datetime import timezone, datetime
from typing import Dict, Optional, TYPE_CHECKING
from bson import ObjectId

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class UserManager:
    class Updater:
        def __init__(self, db: "MongoDBConfig.MongoDB"):
            self.db = db

        # 更新用户密码
        def password(self, userId: str, newPassword: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(userId)
                }
                updateQuery = {
                    "$set": {
                        "password": PasswordHelper.generateHashPassword(newPassword),
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.users.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 更新用户密码失败: { str(e) }")
                return False

        # 更新用户头像
        def avatar(self, userId: str, avatarUrl: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(userId)
                }
                updateQuery = {
                    "$set": {
                        "profile.avatar": avatarUrl,
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.users.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 更新用户头像失败: { str(e) }")
                return False
            
        # 更新用户统计数据
        def stats(self, userId: str, chats: int = 0, messages: int = 0) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(userId)
                }
                incQuery = {}

                if (chats > 0):
                    incQuery["stats.totalChats"] = chats

                if (messages > 0):
                    incQuery["stats.totalMessages"] = messages

                if (not incQuery):
                    logging.warning(f"⚠️ 没有提供任何要增加的统计数据 (userId: { userId })")
                    return False
                
                updateQuery = {
                    "$inc": incQuery,
                    "$set": {
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }

                self.db.users.update_one(idFilter, updateQuery)

                return True
            except Exception as e:
                logging.error(f"❌ 更新用户统计失败: { str(e) }")
                return False

    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db
        self.updater = self.Updater(db)

    # 创建新用户, 返回用户ID
    def createUser(self, name: str, password: str, email: str, gender: str, **kwargs) -> str:
        userData = {

            # 身份凭证
            "name": name, # 昵称
            "email": email, # 邮箱
            "password": PasswordHelper.generateHashPassword(password), # 存储哈希后的密码

            # 用户资料
            "profile": {
                "gender": gender, # 性别
                "avatar": kwargs.get("avatar", ""), # 头像
                "belongGroup": kwargs.get("belongGroup", ""), # 所属分组
            },

            # 账户状态与资源
            "account": {
                "isActive": True, # 登录状态
                "chance": kwargs.get("chance", 10), # 默认机会次数
            },

            # 时间戳
            "timeNode": {
                "createdAt": datetime.now(timezone.utc), # 创建时间
                "updatedAt": datetime.now(timezone.utc) # 更新时间
            },

            # 统计数据
            "stats": {
                "totalChats": 0, # 总聊天次数
                "totalDrawings": 0 # 总绘画次数
            }
        }
        result = self.db.users.insert_one(userData)

        return str(result.inserted_id)
        
    # 验证用户密码
    def verifyPassword(self, name: str, email: str, password: str) -> bool:        
        user = self.getUserByUsername(name) or self.getUserByEmail(email)

        if (not user):
            return False

        return PasswordHelper.verifyHashPassword(password, user.get('password', ''))

    # 根据邮箱获取用户
    def getUserByEmail(self, email: str) -> Optional[Dict]:
        return self.db.users.find_one({
            "email": email, 
            "account.isActive": True
        })
    
    # 根据用户名获取用户
    def getUserByUsername(self, name: str) -> Optional[Dict]:
        return self.db.users.find_one({
            "name": name, 
            "account.isActive": True
        })

    # 根据ID获取用户
    def getUserById(self, userId: str) -> Optional[Dict]:
        try:
            return self.db.users.find_one({
                "_id": ObjectId(userId), 
                "account.isActive": True
            })
        except Exception as e:
            logging.error(f"❌ 根据ID获取用户时发生错误 (userId: { userId }): { str(e) }")

            return None
