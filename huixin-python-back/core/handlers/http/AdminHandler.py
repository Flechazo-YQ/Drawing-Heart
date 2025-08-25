import flask, logging

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.route.ApiState import ApiState
from core.utils.token.AdminTokenHelper import AdminTokenHelper
from core.utils.flask.CommonHelper import CommonHelper

class AdminHandler:
    
    # 处理管理员登录
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.ADMIN_LOGIN.route, methods=ApiState.ADMIN_LOGIN.method)
    def adminLogin():
        data = flask.request.get_json()

        username = data.get('username')
        password = data.get('password')
        
        if (not username or not password):
            return CommonHelper.errorResponse(1, '请提供用户名和密码', 400)

        admin = MongoDBConfig.adminManager.verifyCredentials(username, password)

        # 验证管理员凭证
        if (admin):
            token = AdminTokenHelper.generateAdminToken(username)

            return flask.jsonify({
                'code': 0,
                'message': '登录成功',
                'token': token
            }), 200

        return CommonHelper.errorResponse(1, '用户名或密码错误', 401)

    # 获取管理员信息
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.ADMIN_INFO.route, methods=ApiState.ADMIN_INFO.method)
    @AdminTokenHelper.adminTokenRequired
    def getAdminInfo():
        try:
            admin = flask.g.admin
            adminInfo = {
                'name': admin.get('name'),
                'role': admin.get('role'),
                'lastLogin': admin.get('timeNode', {}).get('lastLoginAt'),
                'stats': admin.get('stats', {}),
                '_id': str(admin.get('_id'))
            }
            
            return flask.jsonify({
                'code': 0,
                'message': '获取管理员信息成功',
                'data': adminInfo
            }), 200
            
        except Exception as e:
            logging.error(f'❌ 获取管理员信息失败: { str(e) }')
            
            return CommonHelper.errorResponse(1, f'获取管理员信息失败: { str(e) }', 500)
