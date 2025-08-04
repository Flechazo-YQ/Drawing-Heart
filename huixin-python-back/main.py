# -*- coding: utf-8 -*-
import core.handlers.api  # 确保导入所有处理器

import os, logging, sys

from core.configs.MongoDBConfig import MongoDBConfig
from core.classifiers.EmotionClassifier import EmotionClassifier
from core.classifiers.DummyClassifier import DummyClassifier
from core.states.GlobalState import GlobalState
from core.states.SocketState import SocketState

# 初始化MongoDB（确保在应用启动时就完成初始化）
try:
    MongoDBConfig.initMongoDB()
    logging.info("MongoDB初始化成功")
except Exception as e:
    logging.error(f"MongoDB初始化失败: { str(e) }")
    raise e

# 注册字体 - 注释掉避免文件不存在错误
# pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))  # 确保路径正确，或使用系统字体路径

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 保存绘画
os.makedirs(GlobalState.SAVE_DIR, exist_ok=True)

if (__name__ == '__main__'):
    GlobalState.APP.jinja_env.variable_start_string = '[['
    GlobalState.APP.jinja_env.variable_end_string = ']]'

    # 初始化情感分析模型
    currentDir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        classifier = EmotionClassifier(
            modelPath=os.path.join(currentDir, "emotion_model"),
            slangFile=os.path.join(currentDir, "slang_map.csv")
        )
        logging.info("✅ 情感分析模型初始化成功")
    except Exception as e:
        logging.error(f"❌ 情感分析模型初始化失败: { str(e) }")

        classifier = DummyClassifier()

        logging.warning("⚠️ 使用虚拟分类器，危险检测功能不可用")
    
    # 通过SocketIO启动应用
    SocketState.socketio.run(
        GlobalState.APP, 
        debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, log_output=True
    )
