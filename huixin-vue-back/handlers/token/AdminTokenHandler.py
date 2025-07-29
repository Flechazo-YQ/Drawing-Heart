import jwt, datetime, flask

from states.TokenState import TokenState
from states.GlobalState import GlobalState

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
            payload = jwt.decode(token, TokenState.HAS_SECRET_KEY, algorithms = [TokenState.ALGORITHM])
            adminUsername = payload['admin_username']

            return adminUsername if adminUsername in TokenState.ADMIN_CREDENTIALS else None

        except jwt.ExpiredSignatureError:
            return None
        
        except jwt.InvalidTokenError:
            return None

    #管理员登录处理
    @classmethod
    @GlobalState.app.route('/api/admin/login', methods = ['POST'])
    def adminLogin(cls):
        data = flask.request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if (not username or not password):
            return flask.jsonify({
                'code': 1,
                'message': '请提供用户名和密码'
            }), 400
        
        # 验证管理员凭证
        if (username in TokenState.ADMIN_CREDENTIALS and TokenState.ADMIN_CREDENTIALS[username] == TokenState.sha256Hash(password)):
            
            # 生成管理员令牌
            token = AdminTokenHandler.generateAdminToken(username)

            return flask.jsonify({
                'code': 0,
                'message': '登录成功',
                'token': token
            }), 200
        
        else:
            return flask.jsonify({
                'code': 1,
                'message': '用户名或密码错误'
            }), 401
