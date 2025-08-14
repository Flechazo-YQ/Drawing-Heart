import functools, flask, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler

class AuthenticateHelper:

    # Socket.IO事件装饰器: 验证管理员是否已在会话中认证
    @staticmethod
    def adminAuthenticated(func):

        @functools.wraps(func)
        def decoratedFunction(*args, **kwargs):
            if ("adminId" not in flask.session):
                logging.warning("⚠️ 管理员未认证，拒绝访问")
                SocketQueueHandler.queueEmit('error', {
                    'message': 'Unauthorized'
                }, sid=flask.request.sid) # type: ignore
                return None

            admin = MongoDBConfig.adminManager.getAdminById(flask.session["adminId"])

            if (not admin):
                logging.error(f"❌ 管理员未找到: { flask.session['adminId'] }")
                SocketQueueHandler.queueEmit('error', {
                    'message': 'Unauthorized'
                }, sid=flask.request.sid) # type: ignore
                return None

            return func(admin=admin, *args, **kwargs)
        return decoratedFunction

    # Socket.IO事件装饰器: 验证用户是否已在会话中认证
    @staticmethod
    def userAuthenticated(func):

        @functools.wraps(func)
        def decoratedFunction(*args, **kwargs):
            if ("userId" not in flask.session):
                logging.warning("⚠️ 用户未认证，拒绝访问")
                SocketQueueHandler.queueEmit('error', {
                    'message': 'Unauthorized'
                }, sid=flask.request.sid) # type: ignore
                return None

            user = MongoDBConfig.userManager.getUserById(flask.session["userId"])

            if (not user):
                logging.error(f"❌ 用户未找到: { flask.session['userId'] }")
                SocketQueueHandler.queueEmit('error', {
                    'message': 'Unauthorized'
                }, sid=flask.request.sid) # type: ignore
                return None

            return func(user=user, *args, **kwargs)
        return decoratedFunction
