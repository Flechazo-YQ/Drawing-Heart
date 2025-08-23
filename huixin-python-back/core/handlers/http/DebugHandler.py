import flask, os

from core.configs.BlueprintConfig import BlueprintConfig
from core.states.route.ApiState import ApiState

class DebugHandler:

    # 调试API: 显示所有相关路径信息
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.DEBUG_PATH['route'], methods=ApiState.DEBUG_PATH['method'])
    def debugPaths():
        configUploadFolder = flask.current_app.config['UPLOAD_FOLDER']
        avatarDir = os.path.join(configUploadFolder, 'avatars') if (configUploadFolder) else '未配置上传目录'
        avatarFiles = []

        if os.path.exists(avatarDir):
            avatarFiles = os.listdir(avatarDir)

        return flask.jsonify({
            'configUploadFolder': configUploadFolder,
            'avatarDirectory': avatarDir,
            'avatarFiles': avatarFiles
        })