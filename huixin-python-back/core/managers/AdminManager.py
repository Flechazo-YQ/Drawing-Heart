import logging

from core.utils.PasswordHelper import PasswordHelper

from datetime import datetime, timezone
from bson import ObjectId
from typing import Dict, List, TYPE_CHECKING

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class AdminManager:
    class Formatter:
        def doc(self, admin: Dict) -> Dict:
            if (admin):
                admin["_id"] = str(admin["_id"])
                admin.pop("password", None)

            return admin

        def list(self, admins: List[Dict]) -> List[Dict]:
            return [self.doc(admin) for admin in admins]

    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db
        self.formatter = self.Formatter()

    # 创建管理员
    def createAdmin(self, name: str, password: str, role: str):
        try:
            idFilter = {
                "name": name
            }

            if (self.db.admins.find_one(idFilter)):
                logging.warning(f"⚠️ 管理员已存在: { name }")
                return None

            adminData = {
                "name": name,
                "password": PasswordHelper.generateHashPassword(password),
                "role": role,
                "stats": {
                    "isActive": True
                },
                "timeNode": {
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc),
                    "lastLoginAt": None
                }
            }
            result = self.db.admins.insert_one(adminData)

            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"❌ 创建管理员失败: { name }, 错误: { str(e) }")
            return None

    # 验证管理员凭据
    def verifyCredentials(self, name: str, password: str):
        try:
            idFilter = {
                "name": name,
                "stats.isActive": True
            },
            updateQuery = {
                "$set": {
                    "timeNode.lastLoginAt": datetime.now(timezone.utc)
                }
            }
            admin = self.db.admins.find_one(idFilter)

            if (admin and PasswordHelper.verifyHashPassword(password, admin["password"])):
                idFilter = {
                    "_id": admin["_id"]
                }
                self.db.admins.update_one(idFilter, updateQuery)
                logging.info(f"✅ 管理员登录成功: { name }")

                return self.formatter.doc(admin)
        except Exception as e:
            logging.error(f"❌ 管理员登录失败: { name }, 错误: { str(e) }")

    # 根据ID获取管理员信息
    def getAdminById(self, adminId: str):
        try:
            idFilter = {
                "_id": ObjectId(adminId)
            }
            admin = self.db.admins.find_one(idFilter)

            return self.formatter.doc(admin) if (admin) else None
        except Exception as e:
            logging.error(f"❌ 获取管理员失败: { adminId }, 错误: { str(e) }")
            return None

    # 获取管理员列表
    def getAdminsList(self):
        try:
            idFilter = {
                "state.isActive": True
            }
            admins = list(self.db.admins.find(idFilter))

            return self.formatter.list(admins)
        except Exception as e:
            logging.error(f"❌ 获取所有管理员列表失败: { str(e) }")
            return []
