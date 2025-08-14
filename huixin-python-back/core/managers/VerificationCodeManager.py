import random, logging

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class VerificationCodeManager:
    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db

    def createCode(self, email: str, purpose: str, ttlMinutes: int = 10):
        try:
            code = ""

            for _ in range(4):
                code += str(random.randint(0, 9))

            expiredAt = datetime.now(timezone.utc) + timedelta(minutes=ttlMinutes)
            emailFilter = {
                "email": email,
                "purpose": purpose
            }
            updateQuery = {
                "$set": {
                    "code": code,
                    "expiredAt": expiredAt,
                    "createAt": datetime.now(timezone.utc)
                }
            }

            self.db.verificationCodeManager.update_one(emailFilter, updateQuery, upsert=True)
            return code
        except Exception as e:
            logging.error(f"❌ 创建验证码失败: { str(e) }")
            return None
        
    def verifyCode(self, email: str, code: str, purpose: str) -> bool:
        try:
            updateQuery = {
                "email": email,
                "code": code,
                "purpose": purpose,
                "expiredAt": {
                    "$gt": datetime.now(timezone.utc)
                }
            }
            result = self.db.verificationCodeManager.find_one_and_delete(updateQuery)

            if (not result):
                logging.warning(f"⚠️ 验证码 { code } for { email } ({ purpose }) 验证失败或已过期。")

            logging.info(f"✅ 验证码 { code } for { email } ({ purpose }) 验证成功。")
            return True
        except Exception as e:
            logging.error(f"❌ 验证码 { code } for { email } ({ purpose }) 验证失败: { str(e) }")
            return False