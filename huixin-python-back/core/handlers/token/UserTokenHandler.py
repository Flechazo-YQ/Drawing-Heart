import datetime, jwt

from core.states.TokenState import TokenState

class UserTokenHandler:
    
    #生成用户JWT
    @staticmethod
    def generateUserToken(userId):
        payload = {
            'user_id': userId,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = TokenState.ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        return jwt.encode(payload, TokenState.HAS_SECRET_KEY, algorithm = TokenState.ALGORITHM)

    #验证用户JWT
    @classmethod
    def verifyUserToken(cls, token):
        try:
            payload = jwt.decode(token, TokenState.HAS_SECRET_KEY, algorithms = [TokenState.ALGORITHM])

            return payload['user_id']
        
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None