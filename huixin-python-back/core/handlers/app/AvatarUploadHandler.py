import logging, os, flask

from core.states.GlobalState import GlobalState

class AvatarUploadHandler:
    
    @staticmethod
    @GlobalState.APP.route('/uploads/<path:filename>')
    def serveUploads(filename: str):
        try:
            pathParts = filename.split('/')

            if (len(pathParts) > 1):
                subdir = os.path.join(GlobalState.UPLOAD_FOLDER, os.path.dirname(filename))
                baseFilename = os.path.basename(filename)

                logging.info(f"提供文件: { subdir }/{ baseFilename }")

                fullPath = os.path.join(subdir, baseFilename)

                if (os.path.exists(fullPath)):
                    logging.info(f"文件存在: { fullPath }")

                    response = flask.send_from_directory(subdir, baseFilename)

                    response.headers['Access-Control-Allow-Origin'] = '*'
                    response.headers['Cache-Control'] = 'public, max-age=86400'

                    return response
                else:
                    logging.warning(f"文件不存在: { fullPath }")

                    return flask.jsonify({
                        'error': '文件不存在'
                    }), 404
                
            logging.info(f"提供文件: { GlobalState.UPLOAD_FOLDER }/{ filename }")

            fullPath = os.path.join(GlobalState.UPLOAD_FOLDER, filename)

            if (os.path.exists(fullPath)):
                logging.info(f"文件存在: { fullPath }")

                response = flask.send_from_directory(GlobalState.UPLOAD_FOLDER, filename)

                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'

                return response
            else:
                logging.warning(f"文件不存在: { fullPath }")

                return flask.jsonify({
                    'error': '文件不存在'
                }), 404
        except Exception as e:
            logging.error(f"提供文件时出错: { str(e) }")
            return flask.jsonify({
                'error': str(e)
            }), 500

