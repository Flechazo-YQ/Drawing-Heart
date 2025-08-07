import os

from flask import Flask
from typing import Final, Optional

class GlobalState:
    userLatestImages = {} # 存储用户的最新图片URL
    userContexts = {} # 存储每个用户的上下文，避免全局变量混乱
    userConnections = {} # 存储用户连接
    userCurrentChats = {} # 存储用户当前活跃聊天ID

    # 存储危险对话
    dangerousChats = {}
    activeAdmins = {}

    sidToUser = {} # 存储sid到用户ID的映射

    URL: Final[str] = "https://api.siliconflow.cn/v1/chat/completions"
    ALLOWED_EXTENSIONS: Final[set] = {'png', 'jpg', 'jpeg', 'gif'} # 允许的文件扩展名
    SAVE_DIR: Final[str] = "saved_drawings" # 保存图片的目录

    # Flask应用实例
    APP: Optional[Flask] = None

    # 情感分析模型 - 延迟初始化，避免启动时就加载模型
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    CLASSIFIER: Optional[object] = None