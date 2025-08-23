import flask

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.route.ApiState import ApiState
from core.utils.PasswordHelper import PasswordHelper
from core.utils.token.UserTokenHelper import UserTokenHelper

class UserAuthHandler:
   
    # 登录处理
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.USER_LOGIN['route'], methods=ApiState.USER_LOGIN['method'])
    def login():
        data = flask.request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user = MongoDBConfig.userManager.getUserByUsername(username) or MongoDBConfig.userManager.getUserByEmail(email)

        # 如果用户名和邮箱都找不到, 返回错误
        if (not user):
            return flask.jsonify({
                'code': 1, 
                'message': '用户名或邮箱不存在'
            })

        # 验证密码
        storedHash = user.get('password', '')

        if (storedHash is None or not PasswordHelper.verifyHashPassword(password, storedHash)):
            return flask.jsonify({
                'code': 1, 
                'message': '密码错误'
            })
        
        # 如果密码正确, 生成用户令牌
        token = UserTokenHelper.generateUserToken(str(user['_id']))

        # 注意：确保返回格式符合前端预期
        return flask.jsonify({
            'code': 0, 
            'message': '登录成功', 
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['name'],
                'email': user['email'],
                'avatar': user.get('profile', {}).get('avatar', '')
            }
        })
    
    # 注册处理
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.USER_REGISTER['route'], methods=ApiState.USER_REGISTER['method'])
    def register():
        data = flask.request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender')
        code = data.get('code')

        if (not all([username, password, email, gender, code])):
            return flask.jsonify({
                'code': 1, 
                'message': '所有字段均为必填项'
            }), 400

        if (not MongoDBConfig.codeManager.verifyCode(email, code, 'register')):
            return flask.jsonify({
                'code': 1, 
                'message': '验证码错误或已过期'
            }), 400
        
        if (MongoDBConfig.userManager.getUserByUsername(username)):
            return flask.jsonify({
                'code': 1, 
                'message': '用户名已存在'
            }), 409

        if (MongoDBConfig.userManager.getUserByEmail(email)):
            return flask.jsonify({
                'code': 1, 
                'message': '邮箱已被注册'
            }), 409

        userId = MongoDBConfig.userManager.createUser(username, password, email, gender)

        if (not userId):
            return flask.jsonify({
                'code': 1, 
                'message': '注册失败, 请稍后重试'
            }), 500

        return flask.jsonify({
            'code': 0, 
            'message': '注册成功'
        }), 201
