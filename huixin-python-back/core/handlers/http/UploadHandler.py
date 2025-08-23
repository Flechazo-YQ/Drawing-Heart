import logging, os, flask

from core.configs.BlueprintConfig import BlueprintConfig
from core.states.route.UploadsState import UploadsState

class UploadHandler:

    # 处理文件上传
    @staticmethod
    @BlueprintConfig.uploadsRoutes(UploadsState.SERVE_UPLOADS['route'])
    def serveUploads(filename: str):
        try:
            uploadFolder = flask.current_app.config['UPLOAD_FOLDER']

            # 构建完整路径
            filename = filename.replace('/', os.sep).replace('\\', os.sep)
            fullPath = os.path.join(uploadFolder, filename)

            if (os.path.isfile(fullPath)):
                response = flask.send_file(fullPath)

                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                response.headers['Access-Control-Allow-Origin'] = '*'

                return response
            
            logging.warning(f"⚠️ 文件不存在: { fullPath }")
            
            return flask.jsonify({
                'error': 'File not found',
                'path': fullPath
            }), 404
                
        except Exception as e:
            logging.error(f"❌ 提供文件时出错: { str(e) }")
            return flask.jsonify({
                'error': f'Server error: { str(e) }'
            }), 500
