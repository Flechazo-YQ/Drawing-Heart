import flask

from core.states.GlobalState import GlobalState
from core.states.TokenState import TokenState
from core.handlers.token.AdminTokenHandler import AdminTokenHandler

class AdminHandler:
    
    @staticmethod
    @GlobalState.APP.route('/api/admin/login', methods=['POST'])
    def adminLogin():
        data = flask.request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if (not username or not password):
            return flask.jsonify({
                'code': 1,
                'message': '请提供用户名和密码'
            }), 400
        
        # 验证管理员凭证
        if (
            username in TokenState.ADMIN_CREDENTIALS 
            and TokenState.ADMIN_CREDENTIALS[username] == TokenState.sha256Hash(password)
        ):
            # 生成管理员令牌
            token = AdminTokenHandler.generateAdminToken(username)

            return flask.jsonify({
                'code': 0,
                'message': '登录成功',
                'token': token
            }), 200
        
        return flask.jsonify({
            'code': 1,
            'message': '用户名或密码错误'
        }), 401
