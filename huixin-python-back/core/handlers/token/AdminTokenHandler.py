import jwt, datetime, flask, functools, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.TokenState import TokenState

from datetime import datetime, timedelta, timezone

class AdminTokenHandler:

    #生成管理员JWT
    @staticmethod
    def generateAdminToken(adminName: str):
        payload = {
            'adminName': adminName,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }

        return jwt.encode(payload, TokenState.SECRET_KEY, algorithm = TokenState.ALGORITHM)

    #验证管理员JWT
    @staticmethod
    def verifyAdminToken(token: str):
        try:
            payload = jwt.decode(token, TokenState.SECRET_KEY, algorithms=[TokenState.ALGORITHM])
            adminName = payload['adminName']

            return adminName if (MongoDBConfig.adminManager.getAdminByName(adminName)) else None

        except jwt.ExpiredSignatureError:
            return None
        
        except jwt.InvalidTokenError:
            return None
        
    # token认证注解
    @classmethod
    def adminTokenRequired(cls, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            token = None

            if ("Authorization" in flask.request.headers):
                authHeader = flask.request.headers["Authorization"]
                token = authHeader.split(" ")[1] if (" " in authHeader) else authHeader

            if (not token):
                if (args and isinstance(args[0], dict) and 'token' in args[0]):
                    token = args[0]['token']

            if (not token):
                return flask.jsonify({
                    "code": 401,
                    "message": "Token is missing!"
                }), 401
            
            try:
                adminName = cls.verifyAdminToken(token)

                if (not adminName):
                    return flask.jsonify({
                        "code": 401,
                        "message": "Invalid or expired token!"
                    }), 401

                admin = MongoDBConfig.adminManager.getAdminByName(adminName)

                if (not admin):
                    return flask.jsonify({
                        "code": 404,
                        "message": "Admin not found!"
                    }), 404

            except Exception as e:
                logging.error(f"❌ Token验证失败: { str(e) }")
                return flask.jsonify({
                    "code": 500,
                    "message": "Internal Server Error"
                }), 500
            
            flask.g.admin = admin
            
            return func(*args, **kwargs)
        return wrapper