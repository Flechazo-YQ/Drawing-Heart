from core.utils.TypedDictionaryHelper import TypedDictionaryHelper

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
    USER_AUTH: Final[str] = "user_auth"
    USER_MESSAGE: Final[str] = "user_message"

    ADMIN_AUTH: Final[str] = "admin_auth"
    ADMIN_MESSAGE: Final[str] = "admin_message"
    ADMIN_REQUEST_HISTORY: Final[str] = "request_history"

    DISCONNECT: Final[str] = "disconnect"

    # 后端Socket事件及数据映射
    REQUEST_HISTORY_RESPONSE: Final[TypedDictionaryHelper.Socket] = {
        "event": "request_history_response",
        "data": TypedDictionaryHelper.RequestHistoryResponseData
    }
    NEW_MESSAGE: Final[TypedDictionaryHelper.Socket] = {
        "event": "new_message",
        "data": TypedDictionaryHelper.NewMessageData
    }
    DANGEROUS_CHATS_LIST: Final[TypedDictionaryHelper.Socket] = {
        "event": "dangerous_chats_list",
        "data": TypedDictionaryHelper.DangerousChatsListData
    }

    ADMIN_MESSAGE_RESPONSE: Final[TypedDictionaryHelper.Socket] = {
        "event": "admin_message_response",
        "data": TypedDictionaryHelper.AdminMessageResponseData
    }
    ADMIN_REPLY: Final[TypedDictionaryHelper.Socket] = {
        "event": "admin_reply",
        "data": TypedDictionaryHelper.AdminReplyData
    }


