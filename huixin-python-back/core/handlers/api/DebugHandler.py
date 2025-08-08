import flask, logging,os

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.api.chat.UserChatHandler import UserChatHandler

class DebugHandler:
        
    #调试API: 检查用户的聊天状态
    @staticmethod
    @BlueprintConfig.apiRoutes('/debug/status', methods=['GET'])
    def debugChatStatus():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 获取用户的当前聊天ID
            currentChat = GlobalState.userCurrentChats.get(userId, "无")

            # 获取用户的上下文长度
            contextLength = len(GlobalState.userContexts.get(userId, []))

            # 获取用户的聊天列表
            userChats = MongoDBConfig.chatManager.getUserChats(userId)

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'user_id': userId,
                    'current_chat_id': currentChat,
                    'context_length': contextLength,
                    'total_chats': len(userChats),
                    'chat_list': [
                        { 
                            'id': str(chat['_id']), 
                            'title': chat['title'] 
                        } for chat in userChats[:5]
                    ]  # 只显示前5个
                }
            })
        
        except Exception as e:
            logging.error(f"获取聊天状态失败: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取聊天状态失败: { str(e) }'
            }), 500
        
    # 调试API: 检查危险检测功能
    @staticmethod
    @BlueprintConfig.apiRoutes('/debug/detection', methods=['POST'])
    def testDangerDetection():
        try:
            data = flask.request.get_json()
            testMessage = data.get('message', '')

            if (not testMessage):
                return flask.jsonify({'error': '消息不能为空'}), 400

            # 直接调用危险检测函数
            dangerScore = UserChatHandler.processMessage(testMessage)

            return flask.jsonify({
                'message': testMessage,
                'danger_score': float(dangerScore),
                'is_dangerous': dangerScore > 0.3,
                'threshold': 0.3
            })
        except Exception as e:
            return flask.jsonify({'error': str(e)}), 500

    # 调试API: 将相对路径转换为绝对URL
    @staticmethod
    @BlueprintConfig.apiRoutes('/debug/url', methods=['POST'])
    def makeAbsoluteUrl(path: str):
        if (not path or path.startswith(('http://', 'https://'))):
            return path
        
        if (not path.startswith('/')):
            path = '/' + path

        # request必须在请求上下文中可用
        baseUrl = flask.request.host_url.rstrip('/')
        return f"{ baseUrl }{ path }"

    # 调试API: 显示所有相关路径信息
    @staticmethod
    @BlueprintConfig.apiRoutes('/debug/paths', methods=['GET'])
    def debugPaths():
        configUploadFolder = flask.current_app.config['UPLOAD_FOLDER']
        avatarDir = os.path.join(configUploadFolder, 'avatars') if (configUploadFolder) else '未配置上传目录'
        avatarFiles = []

        if os.path.exists(avatarDir):
            avatarFiles = os.listdir(avatarDir)

        return flask.jsonify({
            'config_upload_folder': configUploadFolder,
            'avatar_directory': avatarDir,
            'avatar_files': avatarFiles
        })