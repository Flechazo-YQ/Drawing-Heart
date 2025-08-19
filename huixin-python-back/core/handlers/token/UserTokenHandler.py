import datetime, jwt, logging, sys, subprocess, importlib, flask, functools

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.TokenState import TokenState
from core.utils.FormatHelper import FormatHelper

from datetime import datetime, timedelta, timezone
from typing import List

class UserTokenHandler:
    
    #生成用户JWT
    @staticmethod
    def generateUserToken(userId: str | List[str]):
        payload = {
            'userId': userId,
            'exp': datetime.now(timezone.utc) + timedelta(minutes = TokenState.ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        # 兼容Python 3.13的PyJWT库
        try:
            return jwt.encode(payload, TokenState.SECRET_KEY, algorithm = TokenState.ALGORITHM)
        except AttributeError:
            
            # 记录错误
            logging.error("❌ JWT库没有encode方法, 尝试安装PyJWT...")
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyJWT==2.8.0'])
                logging.info("PyJWT安装成功, 正在重新尝试...")
                
                # 重新导入
                importlib.reload(jwt)
                
                # 再次尝试
                return jwt.encode(payload, TokenState.SECRET_KEY, algorithm = TokenState.ALGORITHM)
            except Exception as e:
                logging.error(f"❌ 安装PyJWT失败: { str(e) }")
                raise Exception("无法生成用户令牌, 请确保已安装PyJWT库")

    #验证用户JWT
    @classmethod
    def verifyUserToken(cls, token: str) -> str | None:
        try:
            if (token.startswith('Bearer ')):
                token = token[7:]

            payload = jwt.decode(token, TokenState.SECRET_KEY, algorithms = [TokenState.ALGORITHM])
            userId = payload.get('userId')

            return userId
        
        except jwt.ExpiredSignatureError:
            logging.warning(f"⚠️ 令牌已过期")
            return None
        
        except jwt.InvalidTokenError:
            logging.warning(f"⚠️ 无效的令牌")
            return None
        
        except Exception as e:
            logging.error(f"❌ 验证用户令牌时发生错误: { str(e) }")
            return None
        
    # token认证注解
    @staticmethod
    def userTokenRequired(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            token = flask.request.headers.get('Authorization')
            
            if (not token):
                if (args and isinstance(args[0], dict) and 'token' in args[0]):
                    token = args[0]['token']
            
            if (not token):
                return flask.jsonify({
                    'message': 'Token is missing!'
                }), 401

            userId = UserTokenHandler.verifyUserToken(token)
            
            if (not userId):
                return flask.jsonify({
                    'message': 'Invalid token!'
                }), 401

            user = MongoDBConfig.userManager.getUserById(userId)
            
            if (not user):
                return flask.jsonify({
                    'message': 'User not found!'
                }), 404

            flask.g.user = FormatHelper.json(user)

            return func(*args, **kwargs)
        return wrapper