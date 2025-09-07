import flask

class CommonHelper:

    @staticmethod
    def errorResponse(code: int, message: str, errorCode: int = 400):
        return flask.jsonify({
            'code': code,
            'message': message
        }), errorCode

    @staticmethod
    def successResponse(code: int, message: str, successCode: int = 200):
        return flask.jsonify({
            'code': code,
            'message': message
        }), successCode
    
    