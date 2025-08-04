import flask

from core.states.SocketState import SocketState
from core.states.GlobalState import GlobalState

class ConnectionSocketHandler:

    @staticmethod
    @SocketState.SOCKETIO.on('connect')
    def handleConnect():
        print('Client connected')

    @staticmethod
    @SocketState.SOCKETIO.on('disconnect')
    def handleDisconnect():
        print('Client disconnected')

        #如果是管理员断开连接，更新状态
        sid = flask.request.sid # type: ignore
        
        for adminId, data in GlobalState.activeAdmins.items():
            if (data.get('sid') == sid):
                del GlobalState.activeAdmins[adminId]

                print(f'Admin { adminId } disconnected')

                break