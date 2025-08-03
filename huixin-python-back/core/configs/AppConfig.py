import flask

from core.states.GlobalState import GlobalState

from flask import Response

class AppConfig:

    # 全局OPTIONS处理，支持预检请求
    @staticmethod
    @GlobalState.APP.before_request
    def handlePreflight():
        if (flask.request.method != "OPTIONS"):
            return

        response = Response()

        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")

        return response