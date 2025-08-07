import datetime
import jwt
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

        # 兼容Python 3.13的PyJWT库
        try:
            return jwt.encode(payload, TokenState.HAS_SECRET_KEY, algorithm = TokenState.ALGORITHM)
        except AttributeError:
            # 如果遇到没有encode方法的错误，尝试安装和导入PyJWT
            import sys
            import subprocess
            
            # 记录错误
            logging.error("JWT库没有encode方法，尝试安装PyJWT...")
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyJWT==2.8.0'])
                logging.info("PyJWT安装成功，正在重新尝试...")
                
                # 重新导入
                import importlib
                importlib.reload(jwt)
                
                # 再次尝试
                return jwt.encode(payload, TokenState.HAS_SECRET_KEY, algorithm = TokenState.ALGORITHM)
            except Exception as e:
                logging.error(f"安装PyJWT失败: {str(e)}")
                raise Exception("无法生成用户令牌，请确保已安装PyJWT库")

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