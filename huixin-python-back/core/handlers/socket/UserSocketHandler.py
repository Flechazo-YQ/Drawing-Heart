import flask, flask_socketio, logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.SocketState import SocketState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.utils.AuthenticateHelper import AuthenticateHelper
from core.utils.BroadcastHelper import BroadcastHelper
from core.utils.TypedDictionaryHelper import TypedDictionaryHelper

from typing import Dict

class UserSocketHandler:

    # 处理用户的认证请求
    @staticmethod
    @SocketState.socketio.on(SocketState.USER_AUTH)
    @UserTokenHandler.userTokenRequired
    def handleUserAuth(data: Dict):
        sid = flask.request.sid # type: ignore

        user = flask.g.user
        userId = str(user["_id"])

        UserSocketHandler.__sessionStore(userId)
        UserSocketHandler.__sidAndUserIdStore(userId, sid)

        flask_socketio.join_room(f"user_{ userId }", sid=sid)
        logging.info(f"用户{ userId }(SID: { sid })已认证成功并加入房间{ f'user_{ userId }' }")

    # 处理用户发送的消息
    @staticmethod
    @SocketState.socketio.on(SocketState.USER_MESSAGE)
    @AuthenticateHelper.userAuthenticated
    def handleUserMessage(data: Dict):
        user = flask.g.user
        userId = str(user["_id"])

        chatId = data.get("chatId")
        content = data.get("content")

        if (not chatId or not content):
            logging.error(f"❌ 缺少对话ID或内容")
            return None

        # 处理用户消息
        newMessage = MongoDBConfig.messageManager.createMessage(
            chatId=chatId,
            type="text",
            content=content,
            sender="user"
        )

        if (not newMessage):
            logging.error(f"❌ 创建新消息失败")
            return None

        chats = MongoDBConfig.chatManager.getChatById(chatId)

        if (not chats):
            logging.error(f"❌ 未找到对话: { chatId }")
            return None

        adminId = chats.get("adminId")

        if (not adminId):
            BroadcastHelper.unsignDangerousChats()

            dangerousChatsList: TypedDictionaryHelper.DangerousChatsListData = {
                "chats": chats
            }

            SocketQueueHandler.queueEmit(
                SocketState.DANGEROUS_CHATS_LIST["event"],
                dangerousChatsList,
                room="admin_room"
            )

        adminSid = SocketState.adminIdToSid.get(adminId)
        chatType = chats.get("type", "normal")

        if (chatType == "dangerous" and adminSid):
            BroadcastHelper.signedDangerousChats()

            newMessageData: TypedDictionaryHelper.NewMessageData = {
                "userId": userId,
                "chatId": chatId,
                "role": "user",
                "content": content,
                "timestamp": str(newMessage.get("createdAt", ""))
            }

            SocketQueueHandler.queueEmit(
                SocketState.NEW_MESSAGE["event"], 
                newMessageData,
                sid=adminSid
            )

    # 存储用户id到session
    @staticmethod
    def __sessionStore(userId: str):
        flask.session["userId"] = userId

    # 存储用户sid及id间的映射
    @staticmethod
    def __sidAndUserIdStore(userId: str, sid: str):
        SocketState.userIdToSid[userId] = sid
        SocketState.sidToUserId[sid] = userId
