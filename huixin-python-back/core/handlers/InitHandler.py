import os, logging

from core.classifiers.EmotionClassifier import EmotionClassifier
from core.classifiers.DummyClassifier import DummyClassifier
from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.configs.AppConfig import AppConfig
from core.configs.LogConfig import LogConfig
from core.handlers.ErrorHandler import ErrorHandler
from core.handlers.socket.SocketQueueHandler import SocketQueueHandler
from core.states.DirectoryState import DirectoryState
from core.states.GlobalState import GlobalState
from core.states.SocketState import SocketState
from core.utils.FileHelper import FileHelper

from flask import Flask
from flask_cors import CORS

class InitHandler:

    # 创建Flask应用实例
    @staticmethod
    def initFlaskApp() -> Flask:
        app = Flask(__name__)

        GlobalState.APP = app

        logging.info('✅ Flask应用实例创建成功')
        return app
        
    # 配置App
    @staticmethod
    def configureApp():
        if (not GlobalState.APP):
            raise RuntimeError('❌ Flask App尚未创建。请先调用initFlaskApp。')

        CORS(GlobalState.APP, supports_credentials=True, resources={
            r'/*': {
                'origins': '*',
                'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With']
            }
        })

        GlobalState.APP.jinja_env.variable_start_string = '[['
        GlobalState.APP.jinja_env.variable_end_string = ']]'
        GlobalState.APP.config['UPLOAD_FOLDER'] = FileHelper.getUploadPath()

        AppConfig.registerAppConfig(GlobalState.APP)
        ErrorHandler.registerErrorHandlers(GlobalState.APP)
        BlueprintConfig.registerRoutes(GlobalState.APP)

        logging.info('✅ App配置(CORS, Jinja2, config)完成。')

    # 初始化MongoDB
    @staticmethod
    def initMongoDB():
        try:
            MongoDBConfig.init()
            logging.info('✅ MongoDB初始化成功。')
        except Exception as e:
            logging.error(f'❌ MongoDB初始化失败: { str(e) }')

    # 初始化情感分析模型
    @staticmethod
    def initClassifier():
        if (GlobalState.CLASSIFIER is None):
            try:
                GlobalState.CLASSIFIER = EmotionClassifier(
                    modelPath=os.path.join(DirectoryState.BASE_DIR, 'emotion_model'),
                    slangFile=os.path.join(DirectoryState.BASE_DIR, 'slang_map.csv')
                )
                logging.info('✅ 情感分析模型初始化成功')
            except Exception as e:
                logging.error(f'❌ 情感分析模型初始化失败: { str(e) }')

                GlobalState.CLASSIFIER = DummyClassifier()

                logging.warning('⚠️ 使用虚拟分类器，危险检测功能不可用')

        return GlobalState.CLASSIFIER
    
    # 创建保存目录
    @staticmethod
    def initDrawingSaveDir():
        os.makedirs(DirectoryState.SAVED_DRAWINGS_DIR, exist_ok=True)
        logging.info(f'✅ 绘画保存目录 { DirectoryState.SAVED_DRAWINGS_DIR } 已创建或已存在。')

    # 初始化SocketIO并启动后台任务
    @staticmethod
    def initSocketIO():
        if (not GlobalState.APP):
            raise RuntimeError('❌ Flask App尚未创建。')

        SocketState.socketio.init_app(
            GlobalState.APP,
            cors_allowed_origins = '*',
            async_mode = 'gevent',
            logger = True,
            engineio_logger = True
        )
        SocketState.socketio.start_background_task(target=SocketQueueHandler.socketioBackgroundThread)
        logging.info('✅ Socket.IO后台线程已启动')

    # 初始化所有服务
    @classmethod
    def initAppAndServices(cls):
        LogConfig.initLogging()

        app = cls.initFlaskApp()

        cls.configureApp()
        cls.initMongoDB()
        cls.initClassifier()
        cls.initDrawingSaveDir()
        cls.initSocketIO()
        logging.info('✅ 所有服务已成功初始化，应用准备就绪。')
        return app