import os

from flask import Flask
from typing import Final, Optional

class GlobalState:
    userLatestImages = {} # 存储用户的最新图片URL
    userContexts = {} # 存储每个用户的上下文，避免全局变量混乱
    userConnections = {
        # ‘userId’: {
        #     'sid': flask.request.sid,
        #     'username': username,
        #     'connected_at': datetime.datetime.now().isoformat()
        # }
    }
    userCurrentChats = {} # 存储用户当前活跃聊天ID
    sidToUserId = {} # 存储SID到用户ID的映射
    sidToAdminId = {} # 存储SID到管理员ID的映射

    # 存储危险对话
    dangerousChats = {}
    activeAdmins = {}

    URL: Final[str] = "https://api.siliconflow.cn/v1/chat/completions"
    ALLOWED_EXTENSIONS: Final[set] = {'png', 'jpg', 'jpeg', 'gif'} # 允许的文件扩展名
    SAVE_DIR: Final[str] = "uploads/saved_drawings" # 保存图片的目录

    # Flask应用实例
    APP: Optional[Flask] = None

    # 情感分析模型 - 延迟初始化，避免启动时就加载模型
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    CLASSIFIER: Optional[object] = None