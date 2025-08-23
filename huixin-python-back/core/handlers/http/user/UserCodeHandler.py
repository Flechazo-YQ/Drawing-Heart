import flask, logging

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.route.ApiState import ApiState

class UserCodeHandler:
    
    # 发送注册验证码处理
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.SEND_REGISTER_CODE['route'], methods=ApiState.SEND_REGISTER_CODE['method'])
    def sendRegisterCode():
        data = flask.request.get_json()
        email = data.get('email')

        if (not email):
            return flask.jsonify({
                'code': 1, 
                'message': '邮箱不能为空'
            }), 400

        # 检查邮箱是否已被注册
        if (MongoDBConfig.userManager.getUserByEmail(email)):
            return flask.jsonify({
                'code': 1, 
                'message': '该邮箱已被注册'
            }), 400

        code = MongoDBConfig.codeManager.createCode(email, 'registry')

        if (not code or not MongoDBConfig.codeManager.sendEmailCode(email)):
            logging.error(f'❌ 向 { email } 发送验证码失败')
            return flask.jsonify({
                'code': 1,
                'message': '验证码发送失败, 请稍后重试'
            }), 500

        logging.info(f'向 { email } 发送验证码成功')
        return flask.jsonify({
            'code': 0,
            'message': '验证码已发送, 请注意查收'
        })

    # 发送重置密码验证码处理
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.SEND_RESET_CODE['route'], methods=ApiState.SEND_RESET_CODE['method'])
    def sendResetPasswordCode():
        data = flask.request.get_json()
        email = data.get('email')

        if (not email):
            return flask.jsonify({
                'code': 1,
                'message': '邮箱不能为空'
            }), 400
        
        if (not MongoDBConfig.userManager.getUserByEmail(email)):
            return flask.jsonify({
                'code': 1,
                'message': '该邮箱未注册'
            }), 400

        code = MongoDBConfig.codeManager.createCode(email, 'resetPassword')

        if (not code or not MongoDBConfig.codeManager.sendEmailCode(email)):
            logging.error(f'❌ 向 { email } 发送验证码失败')
            return flask.jsonify({
                'code': 1,
                'message': '验证码发送失败, 请稍后重试'
            }), 500
        
        logging.info(f'向 { email } 发送重置密码验证码: { code }')
        return flask.jsonify({
            'code': 0,
            'message': '验证码已发送, 请注意查收'
        })