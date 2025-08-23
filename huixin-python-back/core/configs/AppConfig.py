import flask, logging

from flask import Response, Flask

class AppConfig:

    # 全局OPTIONS处理，支持预检请求
    @staticmethod
    def handlePreflight():
        if (flask.request.method != "OPTIONS"):
            return

        response = Response()

        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")

        return response
    
    @classmethod
    def registerAppConfig(cls, app: Flask):
        app.before_request(cls.handlePreflight)

        logging.info("✅ 全局配置已注册")

        