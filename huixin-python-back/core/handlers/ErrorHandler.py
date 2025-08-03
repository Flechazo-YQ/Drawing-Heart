import flask

from core.states.GlobalState import GlobalState

class ErrorHandler:

    # 处理400错误
    @staticmethod
    @GlobalState.APP.errorhandler(400)
    def badRequest(error: Exception):
        return flask.jsonify({
            'status': 'error',
            'message': 'Bad Request - 请求格式不正确',
            'code': 400
        }), 400
    
    # 处理404错误
    @staticmethod
    @GlobalState.APP.errorhandler(404)
    def notFound(error: Exception):
        return flask.jsonify({
            'status': 'error', 
            'message': 'Not Found - 请求的资源不存在',
            'code': 404,
            'available_endpoints': {
                '根路径': '/',
                'API登录': '/api/login',
                'API注册': '/api/register'
            }
        }), 404
    
    # 处理500错误
    @staticmethod
    @GlobalState.APP.errorhandler(500)
    def internalServerError(error: Exception):
        return flask.jsonify({
            'status': 'error',
            'message': 'Internal Server Error - 服务器内部错误', 
            'code': 500
        }), 500