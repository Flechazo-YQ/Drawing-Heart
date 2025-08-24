import logging

from core.utils.PasswordHelper import PasswordHelper
from core.utils.FormatHelper import FormatHelper

from datetime import datetime, timezone
from bson import ObjectId
from typing import Dict, List, TYPE_CHECKING

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class AdminManager:
    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db

    # 创建管理员
    def createAdmin(self, name: str, password: str, **kwargs):
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
                "role": kwargs.get("role", "normal"),
                "stats": {
                    "isActive": True
                },
                "timeNode": {
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc),
                    "lastLoginAt": None
                }
            }

            self.db.admins.insert_one(adminData)

            return FormatHelper.jsonOrList(adminData)
        except Exception as e:
            logging.error(f"❌ 创建管理员失败: { name }, 错误: { str(e) }")
            return None

    # 验证管理员凭据
    def verifyCredentials(self, name: str, password: str):
        try:
            idFilter = {
                "name": name,
                "stats.isActive": True
            }
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

                return FormatHelper.jsonOrList(admin)
        except Exception as e:
            logging.error(f"❌ 管理员登录失败: { name }, 错误: { str(e) }")

    # 根据昵称获取管理员信息
    def getAdminByName(self, name: str):
        try:
            nameFilter = {
                "name": name
            }
            admin = self.db.admins.find_one(nameFilter)

            return FormatHelper.jsonOrList(admin) if (admin) else None
        except Exception as e:
            logging.error(f"❌ 获取管理员失败: { name }, 错误: { str(e) }")
            return None

    # 根据ID获取管理员信息
    def getAdminById(self, adminId: str):
        try:
            idFilter = {
                "_id": ObjectId(adminId)
            }
            admin = self.db.admins.find_one(idFilter)

            return FormatHelper.jsonOrList(admin) if (admin) else None
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

            return FormatHelper.jsonOrList(admins)
        except Exception as e:
            logging.error(f"❌ 获取所有管理员列表失败: { str(e) }")
            return []
