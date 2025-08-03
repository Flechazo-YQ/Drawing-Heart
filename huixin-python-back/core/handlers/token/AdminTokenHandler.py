import jwt, datetime

from core.states.TokenState import TokenState
from core.states.GlobalState import GlobalState

class AdminTokenHandler:

    #生成管理员JWT
    @staticmethod
    def generateAdminToken(adminUsername):
        payload = {
            'admin_username': adminUsername,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }

        return jwt.encode(payload, TokenState.HAS_SECRET_KEY, algorithm = TokenState.ALGORITHM)

    #验证管理员JWT
    @staticmethod
    def verifyAdminToken(token):
        try:
            payload = jwt.decode(token, TokenState.HAS_SECRET_KEY, algorithms=[TokenState.ALGORITHM])
            adminUsername = payload['admin_username']

            return adminUsername if (adminUsername in TokenState.ADMIN_CREDENTIALS) else None

        except jwt.ExpiredSignatureError:
            return None
        
        except jwt.InvalidTokenError:
            return None