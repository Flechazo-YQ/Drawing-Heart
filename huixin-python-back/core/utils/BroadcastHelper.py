import logging

from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.states.SocketState import SocketState
from core.utils.type.socket.data.DangerousChatsListData import DangerousChatsListData

class BroadcastHelper:

    # 广播尚未签名的危险对话
    @staticmethod
    def unsignDangerousChats():
        try:
            chats = MongoDBConfig.chatManager.getUnsignedDangerousChats()

            if (not chats): return None

            for (chat) in chats:
                userId = chat.get('userId')
                user = MongoDBConfig.userManager.getUserById(userId) if (userId) else None
                username = user.get('name') if (user is not None) else '未知用户'

                chat['username'] = username

            dangerousChatListData = DangerousChatsListData(
                chats=chats
            )

            SocketQueueHandler.queueEmit(
                SocketState.DANGEROUS_CHATS_LIST.event, 
                dangerousChatListData,
                room='admin_room'
            )
        except Exception as e:
            logging.error(f'❌ 获取未签名危险对话失败: { str(e) }')

    # 对应发送已被签名的危险对话
    @staticmethod
    def signedDangerousChats():
        try:
            chats = MongoDBConfig.chatManager.getSignedDangerousChats()

            if (not chats): return None

            for (chat) in chats:
                userId = chat.get('userId')
                user = MongoDBConfig.userManager.getUserById(userId) if (userId) else None
                username = user.get('name') if (user is not None) else '未知用户'

                chat['username'] = username

                adminId = chat.get('adminId')
                adminSid = SocketState.adminIdToSid.get(adminId)

                SocketQueueHandler.queueEmit('dangerous_chats_list', {
                    'chat': chat if (isinstance(chat, list)) else [chat]
                }, sid=adminSid)
        except Exception as e:
            logging.error(f'❌ 获取已签名危险对话失败: { str(e) }')

