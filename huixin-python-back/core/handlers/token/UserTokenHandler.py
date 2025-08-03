import datetime, jwt
import logging

from core.states.TokenState import TokenState

class UserTokenHandler:
    
    #生成用户JWT
    @staticmethod
    def generateUserToken(userId: str | list[str]):
        payload = {
            'user_id': userId,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = TokenState.ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        return jwt.encode(payload, TokenState.HAS_SECRET_KEY, algorithm = TokenState.ALGORITHM)

    #验证用户JWT
    @classmethod
    def verifyUserToken(cls, token: str):
        try:
            if (token.startswith('Bearer ')):
                token = token[7:]

            payload = jwt.decode(token, TokenState.HAS_SECRET_KEY, algorithms = [TokenState.ALGORITHM])
            userIdData = payload.get('user_id')

            if (isinstance(userIdData, list)):
                return userIdData

            return [userIdData]
        
        except jwt.ExpiredSignatureError:
            logging.warning(f"令牌已过期")
            return None
        
        except jwt.InvalidTokenError:
            logging.warning(f"无效的令牌")
            return None
        
        except Exception as e:
            logging.error(f"验证用户令牌时发生错误: { str(e) }")
            return None