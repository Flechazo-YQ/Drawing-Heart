import flask

from states.SocketState import SocketState
from states.GlobalState import GlobalState

class ConnectionSocketHandler:

    @staticmethod
    @SocketState.socketio.on('connect')
    def handleConnect():
        print('Client connected')

    @staticmethod
    @SocketState.socketio.on('disconnect')
    def handleDisconnect():
        print('Client disconnected')

        #如果是管理员断开连接，更新状态
        sid = flask.request.sid
        
        for adminId, data in GlobalState.activeAdmins.items():
            if (data.get('sid') == sid):
                del GlobalState.activeAdmins[adminId]

                print(f'Admin { adminId } disconnected')

                break