import flask, logging, os, secrets

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.DirectoryState import DirectoryState
from core.states.route.ApiState import ApiState
from core.utils.FileHelper import FileHelper
from core.utils.UrlHelper import UrlHelper
from core.utils.token.UserTokenHelper import UserTokenHelper
from core.utils.flask.CommonHelper import CommonHelper

class UserProfileHandler:

    # 用户头像上传接口
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.UPLOAD_AVATAR.route, methods=ApiState.UPLOAD_AVATAR.method)
    def uploadAvatar():
        token = flask.request.headers.get('Authorization')

        if (not token):            
            return CommonHelper.errorResponse(1, '缺少Authorization令牌', 401)

        userId = UserTokenHelper.verifyUserToken(token)

        if (not userId):
            return CommonHelper.errorResponse(1, '无效的令牌', 401)

        try:
            # 检查是否有文件上传
            if ('avatar' not in flask.request.files):
                return CommonHelper.errorResponse(1, '未上传文件', 400)

            file = flask.request.files['avatar']

            # 检查文件名是否为空
            if (file.filename is None):
                return CommonHelper.errorResponse(1, '未选择文件', 400)

            # 检查文件类型
            if (not FileHelper.isAllowedFile(file.filename)):
                logging.error(f'❌ 头像上传失败: 不支持的文件类型 { file.filename }')
                return CommonHelper.errorResponse(1, '不支持的文件类型, 请上传jpg、jpeg、png或gif格式的图片', 400)

            # 确保目录存在
            avatarDir = os.path.join(flask.current_app.config['UPLOAD_FOLDER'], 'avatars')

            os.makedirs(avatarDir, exist_ok=True)
            
            # 获取用户当前的头像信息，以便后续删除
            user = MongoDBConfig.userManager.getUserById(userId)
            oldAvatarUrl = user.get('avatar') if (user) else None
            
            # 生成唯一文件名，防止文件名冲突
            filename = userId + '_' + secrets.token_hex(16) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(avatarDir, filename)

            # 保存文件
            file.save(filepath)
            
            # 构建新头像的相对URL路径
            newAvatarUrl = DirectoryState.AVATAR_DIR + filename
            
            # 更新数据库中的用户头像URL
            success = MongoDBConfig.userManager.updater.avatar(userId, newAvatarUrl)

            if (not success):
                logging.error(f'❌ 更新用户 { userId } 的头像URL失败')
            
            # 如果数据库更新成功，并且存在旧头像，则删除旧头像文件
            if (success and oldAvatarUrl and oldAvatarUrl.startswith(DirectoryState.AVATAR_DIR)):
                try:
                    # 从相对URL构建旧头像的绝对路径
                    oldAvatarFilename = os.path.basename(oldAvatarUrl)
                    oldAvatarFilepath = os.path.join(avatarDir, oldAvatarFilename)

                    if (os.path.exists(oldAvatarFilepath)):
                        os.remove(oldAvatarFilepath)
                    else:
                        logging.warning(f'⚠️ 旧头像文件不存在，无法删除: { oldAvatarFilepath }')
                except Exception as e:
                    logging.error(f'❌ 删除旧头像文件时出错: { str(e) }')

            return flask.jsonify({
                'code': 0,
                'message': '头像上传成功',
                'data': {
                    'avatarUrl': newAvatarUrl
                }
            })
        except Exception as e:
            logging.error(f'❌ 头像上传错误: { str(e) }')

            return CommonHelper.errorResponse(1, '头像上传失败，请稍后重试', 500)  
    
    # 获取用户名, 并返回JSON格式的响应
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.PROFILE_NAME.route, methods=ApiState.PROFILE_NAME.method)
    @UserTokenHelper.userTokenRequired
    def getUsername():
        user = flask.g.user
        userName = user.get('name')

        return flask.jsonify({
            'username': userName
        })

    # 获取用户详细信息
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.PROFILE_INFO.route, methods=ApiState.PROFILE_INFO.method)
    @UserTokenHelper.userTokenRequired
    def getUserInfo():
        try:
            user = flask.g.user
            profile = user.get('profile', {})
            
            avatarUrl = UrlHelper.getAbsoluteUrl(profile.get('avatar', ''))
            profile['avatar'] = avatarUrl
            user['profile'] = profile

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': user
            })
        except Exception as e:
            return flask.jsonify({
                'error': str(e)
            }), 500
        