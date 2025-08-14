import logging, os, flask, secrets

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.FileHandler import FileHandler

class AvatarUploadHandler:
    
    @staticmethod
    @BlueprintConfig.uploadsRoutes('/<path:filename>')
    def serveUploads(filename: str):
        
        
        try:
            uploadFolder = flask.current_app.config['UPLOAD_FOLDER']
            logging.info(f"请求文件: { filename }, 使用上传目录: { uploadFolder }")

            # 构建完整路径
            logging.info(f"原始文件名: { filename }")
            filename = filename.replace('/', os.sep).replace('\\', os.sep)
            logging.info(f"标准化后的文件名: { filename }")
            fullPath = os.path.join(uploadFolder, filename)
            logging.info(f"尝试提供文件: { fullPath }")

            if (os.path.isfile(fullPath)):
                response = flask.send_file(fullPath)

                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                response.headers['Access-Control-Allow-Origin'] = '*'

                return response
            else:
                logging.warning(f"文件不存在: { fullPath }")
                return flask.jsonify({
                    'error': 'File not found',
                    'path': fullPath
                }), 404
                
        except Exception as e:
            logging.exception(f"提供文件时出错: { str(e) }")
            return flask.jsonify({
                'error': f'Server error: { str(e) }'
            }), 500

    # 用户头像上传接口
    @staticmethod
    @BlueprintConfig.apiRoutes('/avatar/upload', methods=['POST'])
    def uploadAvatar():
        token = flask.request.headers.get('Authorization')

        if (not token):
            logging.error("头像上传失败: 缺少Authorization令牌")
            return flask.jsonify({
                'code': 1, 
                'message': 'Token is missing!'
            }), 401

        logging.info(f"收到头像上传请求，令牌: { token[:15] }...")
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            logging.error(f"头像上传失败: 无效的令牌: { token[:15] }...")
            return flask.jsonify({
                'code': 1, 
                'message': 'Invalid token! 请重新登录'
            }), 401

        try:
            # 检查是否有文件上传
            if ('avatar' not in flask.request.files):
                logging.error("头像上传失败: 请求中没有avatar文件")
                return flask.jsonify({
                    'code': 1, 
                    'message': '没有上传文件'
                }), 400

            file = flask.request.files['avatar']

            # 检查文件名是否为空
            if (file.filename == None):
                logging.error("头像上传失败: 文件名为空")
                return flask.jsonify({
                    'code': 1, 
                    'message': '未选择文件'
                }), 400

            # 检查文件类型
            if (not FileHandler.allowedFile(file.filename)):
                logging.error(f"头像上传失败: 不支持的文件类型 { file.filename }")
                return flask.jsonify({
                    'code': 1, 
                    'message': '不支持的文件类型，请上传jpg、jpeg、png或gif格式的图片'
                }), 400

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
            logging.info(f"新头像文件已保存到: { filepath }")
            
            # 构建新头像的相对URL路径
            newAvatarUrl = f'/uploads/avatars/{ filename }'
            
            # 更新数据库中的用户头像URL
            success = MongoDBConfig.userManager.updater.avatar(userId, newAvatarUrl)

            if (not success):
                logging.error(f"更新用户 { userId } 的头像URL失败")
                # 注意：即使数据库更新失败，新文件也已保存，但此处不回滚，以防逻辑复杂化
            
            # 如果数据库更新成功，并且存在旧头像，则删除旧头像文件
            if (success and oldAvatarUrl and oldAvatarUrl.startswith('/uploads/avatars/')):
                try:
                    # 从相对URL构建旧头像的绝对路径
                    oldAvatarFilename = os.path.basename(oldAvatarUrl)
                    oldAvatarFilepath = os.path.join(avatarDir, oldAvatarFilename)

                    if os.path.exists(oldAvatarFilepath):
                        os.remove(oldAvatarFilepath)
                        logging.info(f"成功删除旧头像文件: { oldAvatarFilepath }")
                    else:
                        logging.warning(f"旧头像文件不存在，无法删除: { oldAvatarFilepath }")
                except Exception as e:
                    logging.error(f"删除旧头像文件时出错: { str(e) }")

            logging.info(f"用户 { userId } 头像上传成功: { filename }, URL: { newAvatarUrl }")

            # 测试文件是否可访问
            fileExists = os.path.exists(filepath)
            logging.info(f"新头像文件存在性检查: { filepath } 存在={ fileExists }")

            return flask.jsonify({
                'code': 0,
                'message': '头像上传成功',
                'data': {
                    'avatarUrl': newAvatarUrl
                }
            })
        except Exception as e:
            logging.error(f"头像上传错误: { str(e) }")
            return flask.jsonify({
                'code': 1, 
                'message': f'头像上传失败: { str(e) }'
            }), 500   
