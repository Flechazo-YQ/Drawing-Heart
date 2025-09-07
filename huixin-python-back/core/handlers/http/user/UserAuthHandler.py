import flask

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.route.ApiState import ApiState
from core.utils.PasswordHelper import PasswordHelper
from core.utils.token.UserTokenHelper import UserTokenHelper
from core.utils.flask.CommonHelper import CommonHelper

class UserAuthHandler:
   
    # 登录处理
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.USER_LOGIN.route, methods=ApiState.USER_LOGIN.method)
    def login():
        data = flask.request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        user = MongoDBConfig.userManager.getUserByUsername(username) or MongoDBConfig.userManager.getUserByEmail(email)

        # 如果用户名和邮箱都找不到, 返回错误
        if (not user):
            return CommonHelper.errorResponse(1, '用户名或邮箱不存在')

        # 验证密码
        storedHash = user.get('password', '')

        if (storedHash is None or not PasswordHelper.verifyHashPassword(password, storedHash)):
            return CommonHelper.errorResponse(1, '密码错误')

        # 如果密码正确, 生成用户令牌
        userId = str(user['_id'])
        token = UserTokenHelper.generateUserToken(userId)

        # 注意：确保返回格式符合前端预期
        return flask.jsonify({
            'code': 0, 
            'message': '登录成功', 
            'token': token,
            'user': {
                'id': userId,
                'username': user['name'],
                'email': user['email'],
                'avatar': user.get('profile', {}).get('avatar', '')
            }
        })
    
    # 注册处理
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.USER_REGISTER.route, methods=ApiState.USER_REGISTER.method)
    def register():
        data = flask.request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender')
        code = data.get('code')

        if (not all([username, password, email, gender, code])):
            return CommonHelper.errorResponse(1, '所有字段均为必填项')

        if (not MongoDBConfig.codeManager.verifyCode(email, code, 'register')):
            return CommonHelper.errorResponse(1, '验证码错误或已过期')

        if (MongoDBConfig.userManager.getUserByUsername(username)):
            return CommonHelper.errorResponse(1, '用户名已存在', 409)

        if (MongoDBConfig.userManager.getUserByEmail(email)):
            return CommonHelper.errorResponse(1, '邮箱已被注册', 409)

        userId = MongoDBConfig.userManager.createUser(username, password, email, gender)

        if (not userId):
            return CommonHelper.errorResponse(1, '注册失败, 请稍后重试', 500)

        return CommonHelper.successResponse(0, '注册成功', 201)
