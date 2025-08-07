import flask, logging

from flask import Flask

class ErrorHandler:

    # 处理400错误
    @staticmethod
    def badRequest(error: Exception):
        return flask.jsonify({
            'status': 'error',
            'message': 'Bad Request - 请求格式不正确',
            'code': 400
        }), 400
    
    # 处理404错误
    @staticmethod
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
    def internalServerError(error: Exception):
        return flask.jsonify({
            'status': 'error',
            'message': 'Internal Server Error - 服务器内部错误', 
            'code': 500
        }), 500
    
    @classmethod
    def registerErrorHandlers(cls, app: Flask):
        app.register_error_handler(400, cls.badRequest)
        app.register_error_handler(404, cls.notFound)
        app.register_error_handler(500, cls.internalServerError)

        logging.info("✅ 错误处理器已注册")

        