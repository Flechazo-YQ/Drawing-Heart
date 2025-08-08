import jwt, datetime

from core.states.TokenState import TokenState

class AdminTokenHandler:

    #生成管理员JWT
    @staticmethod
    def generateAdminToken(adminId: str):
        payload = {
            'admin_id': adminId,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }

        return jwt.encode(payload, TokenState.SECRET_KEY, algorithm = TokenState.ALGORITHM)

    #验证管理员JWT
    @staticmethod
    def verifyAdminToken(token: str):
        try:
            payload = jwt.decode(token, TokenState.SECRET_KEY, algorithms=[TokenState.ALGORITHM])
            adminId = payload['admin_id']

            return adminId if (adminId in TokenState.ADMIN_CREDENTIALS) else None

        except jwt.ExpiredSignatureError:
            return None
        
        except jwt.InvalidTokenError:
            return None