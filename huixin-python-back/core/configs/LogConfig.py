import os, logging, sys, re

from logging.handlers import TimedRotatingFileHandler
from logging import Formatter, StreamHandler, FileHandler
from typing import Final
from re import Pattern

class LogConfig:
    LOG_DIR: Final[str] = 'logs'

    class StripAnsiFormatter(Formatter):
        ANSI_REGEX: Final[Pattern] = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        def format(self, record):
            formattedMessage = super().format(record)
            return self.ANSI_REGEX.sub('', formattedMessage)

    @classmethod
    def initLogging(cls):
        try:
            os.makedirs(cls.LOG_DIR, exist_ok=True)

            for filename in os.listdir(cls.LOG_DIR):
                if (filename.endswith('.log')):
                    filePath = os.path.join(cls.LOG_DIR, filename)

                    try:
                        if (os.path.isfile(filePath) or os.path.islink(filePath)):
                            with open(filePath, "w") as f:
                                pass
                    except Exception as e:
                        logging.error(f"❌ 无法清空旧日志文件 { filePath }: { str(e) }")

            fileLogFormatter = cls.StripAnsiFormatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            consoleLogFormatter = Formatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            rootLogger = logging.getLogger()

            rootLogger.setLevel(logging.INFO)

            # 清除已有的处理器, 避免重复添加
            if (rootLogger.hasHandlers()):
                rootLogger.handlers.clear()

            # 控制台日志记录
            consoleHandler = StreamHandler()

            consoleHandler.setFormatter(consoleLogFormatter)
            rootLogger.addHandler(consoleHandler)

            # 总日志文件记录
            appLogHandler = TimedRotatingFileHandler(
                os.path.join(LogConfig.LOG_DIR, "app.log"),
                when="midnight", interval=1, backupCount=30, encoding='utf-8'
            )

            appLogHandler.setFormatter(fileLogFormatter)
            rootLogger.addHandler(appLogHandler)

            # INFO日志文件记录
            infoLogHandler = TimedRotatingFileHandler(
                os.path.join(LogConfig.LOG_DIR, "info.log"),
                when="midnight", interval=1, backupCount=30, encoding='utf-8'
            )

            infoLogHandler.setFormatter(fileLogFormatter)
            infoLogHandler.addFilter(lambda record: record.levelno == logging.INFO)
            rootLogger.addHandler(infoLogHandler)

            # WARNING日志文件记录
            warningLogHandler = TimedRotatingFileHandler(
                os.path.join(LogConfig.LOG_DIR, "warning.log"),
                when="midnight", interval=1, backupCount=30, encoding='utf-8'
            )

            warningLogHandler.setFormatter(fileLogFormatter)
            warningLogHandler.addFilter(lambda record: record.levelno == logging.WARNING)
            rootLogger.addHandler(warningLogHandler)

            # ERROR日志文件记录
            errorLogHandler = TimedRotatingFileHandler(
                os.path.join(LogConfig.LOG_DIR, "error.log"),
                when="midnight", interval=1, backupCount=30, encoding='utf-8'
            )

            errorLogHandler.setFormatter(fileLogFormatter)
            errorLogHandler.setLevel(logging.ERROR)
            rootLogger.addHandler(errorLogHandler)

            logging.info("✅ 日志系统初始化成功")
        except Exception as e:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    FileHandler('app.log', encoding='utf-8'),
                    StreamHandler(sys.stdout)
                ]
            )
            logging.error(f"❌ 初始化自定义日志系统失败: { str(e) }")
