import os

from typing import Final, Set

class FileHelper:

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS: Final[Set[str]] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 检查文件类型是否允许
    @classmethod
    def isAllowedFile(cls, filename: str):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS

    # 查找项目根目录
    @staticmethod
    def findProjectRoot(currentDir=None, depth=0, maxDepth=10):
        if (currentDir is None):
            currentDir = os.getcwd()

        if (depth > maxDepth):
            return os.getcwd()

        if (os.path.basename(currentDir) == 'Drawing-Heart-main'):
            return currentDir

        if (os.path.exists(os.path.join(currentDir, 'huixin-python-back'))):
            return currentDir
        
        parentDir = os.path.dirname(currentDir)

        if (parentDir == currentDir):
            return os.getcwd()
        
        return FileHelper.findProjectRoot(parentDir, depth + 1, maxDepth)

    # 获取上传项目的路径
    @classmethod
    def getUploadPath(cls):
        projectRoot = cls.findProjectRoot()

        if (projectRoot):
            uploadPath = os.path.join(projectRoot, 'huixin-python-back', 'uploads')

            os.makedirs(uploadPath, exist_ok=True)
            os.makedirs(os.path.join(uploadPath, 'avatars'), exist_ok=True)

            return uploadPath
        
        uploadPath = os.path.join(os.getcwd(), 'uploads')

        os.makedirs(uploadPath, exist_ok=True)
        os.makedirs(os.path.join(uploadPath, 'avatars'), exist_ok=True)

        return uploadPath
        