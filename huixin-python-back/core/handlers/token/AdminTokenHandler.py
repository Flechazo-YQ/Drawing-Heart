import jwt, datetime, flask, functools

from core.configs.MongoDBConfig import MongoDBConfig
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
        
    # token认证注解
    @classmethod
    def adminTokenRequired(cls, func):

        @functools.wraps(func)
        def decoratedFunction(*args, **kwargs):
            token = None

            if ("Authorization" in flask.request.headers):
                token = flask.request.headers["Authorization"].split(" ")[1]

            if (not token):
                return flask.jsonify({
                    "code": 401,
                    "message": "Token is missing!"
                }), 401
            
            try:
                adminId = cls.verifyAdminToken(token)

                if (not adminId):
                    return flask.jsonify({
                        "code": 401,
                        "message": "Invalid or expired token!"
                    }), 401
                
                admin = MongoDBConfig.adminManager.getAdminById(adminId)

                if (not admin):
                    return flask.jsonify({
                        "code": 404,
                        "message": "Admin not found!"
                    }), 404

            except Exception as e:
                return flask.jsonify({
                    "code": 500,
                    "message": "Internal Server Error"
                }), 500

            return func(admin=admin, *args, **kwargs)
        return decoratedFunction