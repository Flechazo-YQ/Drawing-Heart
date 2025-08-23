from core.utils.type.socket.EventDict import EventDict
from core.utils.type.socket.data.AdminMessageResponseData import AdminMessageResponseData
from core.utils.type.socket.data.AdminReplyData import AdminReplyData
from core.utils.type.socket.data.DangerousChatsListData import DangerousChatsListData
from core.utils.type.socket.data.NewMessageData import NewMessageData
from core.utils.type.socket.data.RequestHistoryResponseData import RequestHistoryResponseData

from queue import Queue
from flask_socketio import SocketIO
from typing import Final

class SocketState:
    socketio = SocketIO()
    socketioTaskQueue = Queue()

    sidToUserId = {}
    userIdToSid = {}

    sidToAdminId = {}
    adminIdToSid = {}

    # 前端Socket事件
    USER_AUTH: Final[str] = 'user_auth'
    USER_MESSAGE: Final[str] = 'user_message'

    ADMIN_AUTH: Final[str] = 'admin_auth'
    ADMIN_MESSAGE: Final[str] = 'admin_message'
    ADMIN_REQUEST_HISTORY: Final[str] = 'request_history'

    DISCONNECT: Final[str] = 'disconnect'

    # 后端Socket事件及数据映射
    REQUEST_HISTORY_RESPONSE: Final[EventDict] = {
        'event': 'request_history_response',
        'data': RequestHistoryResponseData
    }
    NEW_MESSAGE: Final[EventDict] = {
        'event': 'new_message',
        'data': NewMessageData
    }
    DANGEROUS_CHATS_LIST: Final[EventDict] = {
        'event': 'dangerous_chats_list',
        'data': DangerousChatsListData
    }

    ADMIN_MESSAGE_RESPONSE: Final[EventDict] = {
        'event': 'admin_message_response',
        'data': AdminMessageResponseData
    }
    ADMIN_REPLY: Final[EventDict] = {
        'event': 'admin_reply',
        'data': AdminReplyData
    }


