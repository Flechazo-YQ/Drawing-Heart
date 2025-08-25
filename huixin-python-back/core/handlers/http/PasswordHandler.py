import logging, flask

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.route.ApiState import ApiState
from core.utils.PasswordHelper import PasswordHelper
from core.utils.token.UserTokenHelper import UserTokenHelper
from core.utils.flask.CommonHelper import CommonHelper

class PasswordHandler:

    # 重置密码
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.PASSWORD_RESET.route, methods=ApiState.PASSWORD_RESET.method)
    def resetPassword():
        try:
            data = flask.request.get_json()
            email = data.get('email')
            
            if (not email):
                return CommonHelper.errorResponse(1, '请提供邮箱地址', 400)

            user = MongoDBConfig.userManager.getUserByEmail(email)

            if (not user):
                return CommonHelper.errorResponse(1, '该邮箱未注册', 404)

            code = MongoDBConfig.codeManager.createCode(email, 'reset_password')

            if (not code):
                return CommonHelper.errorResponse(1, '创建验证码失败', 500)

            MongoDBConfig.codeManager.sendEmailCode(email, code)

            return CommonHelper.successResponse(0, '重置密码链接已发送到您的邮箱', 200)

        except Exception as e:
            logging.error(f"❌ 重置密码错误: { str(e) }")

            return CommonHelper.errorResponse(1, '重置密码失败，请稍后重试', 500)

    # 更新密码
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.PASSWORD_UPDATE.route, methods=ApiState.PASSWORD_UPDATE.method)
    def updatePassword():
        try:
            data = flask.request.get_json()
            token = data.get('token')
            newPassword = data.get('password')

            if (not all([token, newPassword])):
                return CommonHelper.errorResponse(1, '请提供所有必需的字段', 400)

            # 验证token
            userId = UserTokenHelper.verifyUserToken(token)

            if (not userId):
                return CommonHelper.errorResponse(1, '无效或过期的重置链接', 401)
                
            # 更新密码
            success = MongoDBConfig.userManager.updater.password(userId, PasswordHelper.generateHashPassword(newPassword))

            if (not success):
                return CommonHelper.errorResponse(1, '用户不存在或更新失败', 404)

            return CommonHelper.successResponse(0, '密码更新成功', 200)
                
        except Exception as e:
            logging.error(f"❌ 更新密码错误: { str(e) }")

            return CommonHelper.errorResponse(1, '更新密码失败，请稍后重试', 500)

    # 直接重置密码
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.PASSWORD_RESET_DIRECT.route, methods=ApiState.PASSWORD_RESET_DIRECT.method)
    def resetPasswordDirect():
        try:
            data = flask.request.get_json()
            email = data.get('email')
            newPassword = data.get('password')

            if (not all([email, newPassword])):
                return CommonHelper.errorResponse(1, '请提供邮箱和新密码', 400)

            # 检查邮箱是否存在
            user = MongoDBConfig.userManager.getUserByEmail(email)

            if (not user):
                return CommonHelper.errorResponse(1, '该邮箱未注册', 404)

            userId = str(user['_id'])

            # 更新密码
            success = MongoDBConfig.userManager.updater.password(userId, PasswordHelper.generateHashPassword(newPassword))

            if (not success):
                return CommonHelper.errorResponse(1, '密码重置失败', 500)

            return CommonHelper.successResponse(0, '密码重置成功', 200)
                
        except Exception as e:
            logging.error(f"❌ 重置密码错误: { str(e) }")

            return CommonHelper.errorResponse(1, '重置密码失败，请稍后重试', 500)


