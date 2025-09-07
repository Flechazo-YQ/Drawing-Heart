import os, logging, sys, re

from logging.handlers import TimedRotatingFileHandler
from logging import Formatter, StreamHandler, FileHandler, Logger
from typing import Final
from re import Pattern

class LogConfig:
    LOG_DIR: Final[str] = 'logs'

    @classmethod
    def initLogging(cls):
        try:
            os.makedirs(cls.LOG_DIR, exist_ok=True)

            cls.__clearOldLogs()

            fileLogFormatter = cls.__StripAnsiFormatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            consoleLogFormatter = cls.__StripAnsiFormatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            rootLogger = logging.getLogger()

            rootLogger.setLevel(logging.INFO)

            # 清除已有的处理器, 避免重复添加
            if (rootLogger.hasHandlers()):
                rootLogger.handlers.clear()

            cls.__addConsoleHandler(rootLogger, consoleLogFormatter)
            cls.__addAppLogHandler(rootLogger, fileLogFormatter)
            cls.__addInfoLogHandler(rootLogger, fileLogFormatter)
            cls.__addWarningLogHandler(rootLogger, fileLogFormatter)
            cls.__addErrorLogHandler(rootLogger, fileLogFormatter)

            logging.info('✅ 日志系统初始化成功')
        except Exception as e:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    FileHandler('app.log', encoding='utf-8'),
                    StreamHandler(sys.stdout)
                ]
            )
            logging.error(f'❌ 初始化自定义日志系统失败: { str(e) }')

    @classmethod
    def __clearOldLogs(cls):
        try:
            for filename in os.listdir(cls.LOG_DIR):
                if (filename.endswith('.log')):
                    filePath = os.path.join(cls.LOG_DIR, filename)

                    try:
                        if (os.path.isfile(filePath) or os.path.islink(filePath)):
                            with open(filePath, 'w') as f:
                                pass
                    except Exception as e:
                        logging.error(f'❌ 无法清空旧日志文件 { filePath }: { str(e) }')
        except Exception as e:
            logging.error(f'❌ 清理旧日志文件失败: { str(e) }')

    # 控制台日志记录
    @staticmethod
    def __addConsoleHandler(logger: Logger, formatter: Formatter):
        consoleHandler = StreamHandler()

        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)

    # 总日志文件记录
    @classmethod
    def __addAppLogHandler(cls, logger: Logger, formatter: Formatter):
        appLogHandler = TimedRotatingFileHandler(
            os.path.join(cls.LOG_DIR, 'app.log'),
            when='midnight', interval=1, backupCount=30, encoding='utf-8'
        )

        appLogHandler.setFormatter(formatter)
        logger.addHandler(appLogHandler)

    # INFO日志文件记录
    @classmethod
    def __addInfoLogHandler(cls, logger: Logger, formatter: Formatter):
        infoLogHandler = TimedRotatingFileHandler(
            os.path.join(cls.LOG_DIR, 'info.log'),
            when='midnight', interval=1, backupCount=30, encoding='utf-8'
        )

        infoLogHandler.setFormatter(formatter)
        infoLogHandler.addFilter(lambda record: record.levelno == logging.INFO)
        logger.addHandler(infoLogHandler)

    # WARNING日志文件记录
    @classmethod
    def __addWarningLogHandler(cls, logger: Logger, formatter: Formatter):
        warningLogHandler = TimedRotatingFileHandler(
            os.path.join(cls.LOG_DIR, 'warning.log'),
            when='midnight', interval=1, backupCount=30, encoding='utf-8'
        )

        warningLogHandler.setFormatter(formatter)
        warningLogHandler.addFilter(lambda record: record.levelno == logging.WARNING)
        logger.addHandler(warningLogHandler)

    # ERROR日志文件记录
    @classmethod
    def __addErrorLogHandler(cls, logger: Logger, formatter: Formatter):
        errorLogHandler = TimedRotatingFileHandler(
            os.path.join(cls.LOG_DIR, 'error.log'),
            when='midnight', interval=1, backupCount=30, encoding='utf-8'
        )

        errorLogHandler.setFormatter(formatter)
        errorLogHandler.setLevel(logging.ERROR)
        logger.addHandler(errorLogHandler)

    class __StripAnsiFormatter(Formatter):
        ANSI_REGEX: Final[Pattern] = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        def format(self, record):
            formattedMessage = super().format(record)
            return self.ANSI_REGEX.sub('', formattedMessage)
