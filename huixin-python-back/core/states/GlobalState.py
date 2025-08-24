from core.classifiers.DummyClassifier import DummyClassifier
from core.classifiers.EmotionClassifier import EmotionClassifier

from flask import Flask
from typing import Final, Optional

class GlobalState:
    URL: Final[str] = "https://api.siliconflow.cn/v1/chat/completions"
    ALLOWED_EXTENSIONS: Final[set] = {'png', 'jpg', 'jpeg', 'gif'} # 允许的文件扩展名

    # Flask应用实例
    APP: Optional[Flask] = None

    # 情感分析模型 - 延迟初始化，避免启动时就加载模型
    CLASSIFIER: Optional[EmotionClassifier | DummyClassifier] = None