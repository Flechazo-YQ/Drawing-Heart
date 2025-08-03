import os

from core.classifiers.EmotionClassifier import EmotionClassifier

from flask import Flask
from typing import Final
from flask_cors import CORS
from torchvision import transforms

class GlobalState:
    userLatestImages = {} # 存储用户的最新图片URL
    userContexts = {} # 存储每个用户的上下文，避免全局变量混乱
    userConnections = {} # 存储用户连接
    userCurrentChats = {} # 存储用户当前活跃聊天ID

    # 存储危险对话
    dangerousChats = {}
    activeAdmins = {}

    URL: Final[str] = "https://api.siliconflow.cn/v1/chat/completions"

    API_KEY: Final[str] = "2n6cCLk2oHeKUWVC8oVaNOHM"
    SECRET_KEY: Final[str] = "4sL409ZBtELNDfQZcJRACg6lICmUX6zs"

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS: Final[set] = {'png', 'jpg', 'jpeg', 'gif'}

    # 保存图片的目录
    SAVE_DIR: Final[str] = "saved_drawings"

    # 保存目录
    UPLOAD_FOLDER: Final[str] = 'uploads'

    APP: Final[Flask] = Flask(__name__)
    APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # 情感分析模型
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    CLASSIFIER: Final[EmotionClassifier] = EmotionClassifier(
        modelPath=os.path.join(BASE_DIR, "emotion_model"),
        slangFile=os.path.join(BASE_DIR, "slang_map.csv")
    )

    # 配置更详细的CORS设置以支持移动端
    CORSMOBILE: Final[CORS] = CORS(APP, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        }
    })

    TRANSFORM: Final[transforms.Compose] = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])