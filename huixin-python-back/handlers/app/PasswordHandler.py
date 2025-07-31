import logging, flask

from handlers.token.UserTokenHandler import UserTokenHandler
from states.GlobalState import GlobalState
from states.TokenState import TokenState

from mongodb_config import user_manager

class PasswordHandler:

    # 重置密码
    @staticmethod
    @GlobalState.app.route('/api/reset-password', methods=['POST'])
    def resetPassword():
        try:
            data = flask.request.get_json()
            email = data.get('email')
            
            if (not email):
                return flask.jsonify({
                    'code': 1,
                    'message': '请提供邮箱地址'
                }), 400
                
            user = user_manager.get_user_by_email(email)

            if (not user):
                return flask.jsonify({
                    'code': 1,
                    'message': '该邮箱未注册'
                }), 404
                    
            # 生成重置密码的token
            reset_token = UserTokenHandler.generateUserToken([str(user['_id']), user['username']])
            
            # TODO: 发送重置密码邮件
            # 这里应该实现发送邮件的功能
            # 为了演示，我们直接返回成功

            return flask.jsonify({
                'code': 0,
                'message': '重置密码链接已发送到您的邮箱'
            }), 200
                
        except Exception as e:
            logging.error(f"重置密码错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': '重置密码失败，请稍后重试'
            }), 500
        
    # 更新密码
    @staticmethod
    @GlobalState.app.route('/api/update-password', methods=['POST'])
    def updatePassword():
        try:
            data = flask.request.get_json()
            token = data.get('token')
            newPassword = data.get('password')

            if (not all([token, newPassword])):
                return flask.jsonify({
                    'code': 1,
                    'message': '请提供所有必需的字段'
                }), 400
                
            # 验证token
            userId = UserTokenHandler.verifyUserToken(token)

            if (not userId):
                return flask.jsonify({
                    'code': 1,
                    'message': '无效或过期的重置链接'
                }), 401
                
            # 更新密码
            success = user_manager.update_user(userId[0], {
                'password': TokenState.sha256Hash(newPassword)
            })
            
            if (success):
                return flask.jsonify({
                    'code': 0,
                    'message': '密码更新成功'
                }), 200
            else:
                return flask.jsonify({
                    'code': 1,
                    'message': '用户不存在或更新失败'
                }), 404
                
        except Exception as e:
            logging.error(f"更新密码错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': '更新密码失败，请稍后重试'
            }), 500
        
    # 直接重置密码
    @staticmethod
    @GlobalState.app.route('/api/reset-password-direct', methods=['POST'])
    def resetPasswordDirect():
        try:
            data = flask.request.get_json()
            email = data.get('email')
            new_password = data.get('password')
            
            if (not all([email, new_password])):
                return flask.jsonify({
                    'code': 1,
                    'message': '请提供邮箱和新密码'
                }), 400
                
            # 检查邮箱是否存在
            user = user_manager.get_user_by_email(email)

            if (not user):
                return flask.jsonify({
                    'code': 1,
                    'message': '该邮箱未注册'
                }), 404
                
            # 更新密码
            success = user_manager.update_user(str(user['_id']), {
                'password': TokenState.sha256Hash(new_password)
            })

            if (success):
                return flask.jsonify({
                    'code': 0,
                    'message': '密码重置成功'
                }), 200
            else:
                return flask.jsonify({
                    'code': 1,
                    'message': '密码重置失败'
                }), 500
                
        except Exception as e:
            logging.error(f"重置密码错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': '重置密码失败，请稍后重试'
            }), 500