import logging

from pymongo import MongoClient

class MongoDBConfig:

    @classmethod
    def initMongoDB(cls, connectionString="mongodb://localhost:27017/", databaseName="huixin_db"):
        from core.managers.UserManager import UserManager
        from core.managers.ChatManager import ChatManager
        from core.managers.MessageManager import MessageManager
        from core.managers.DrawingAnalysisManager import DrawingAnalysisManager

        cls.mongoDb = cls.MongoDB(connectionString, databaseName)
        cls.userManager = UserManager(cls.mongoDb)
        cls.chatManager = ChatManager(cls.mongoDb)
        cls.messageManager = MessageManager(cls.mongoDb)
        cls.drawingAnalysisManager = DrawingAnalysisManager(cls.mongoDb)

        logging.info("MongoDB初始化完成")
        return cls.mongoDb

    class MongoDB:

        # 初始化MongoDB连接
        def __init__(self, connectionString="mongodb://localhost:27017/", databaseName="huixin_db"):
            try:
                self.client = MongoClient(connectionString)
                self.db = self.client[databaseName]

                # 测试连接
                self.client.server_info()
                logging.info(f"成功连接到MongoDB数据库: { databaseName }")
            except Exception as e:
                logging.error(f"连接MongoDB失败: { str(e) }")
                raise e
            
            # 获取集合
            self.users = self.db.users
            self.chats = self.db.chats
            self.messages = self.db.messages
            self.drawingAnalyses = self.db.drawing_analyses  # 新增：绘画分析结果集合
            
            # 创建索引
            self.createIndexes()

        # 创建索引以优化查询性能
        def createIndexes(self):
            try:
                # 用户集合索引
                self.users.create_index("email", unique=True)
                self.users.create_index("username")
                
                # 对话集合索引
                self.chats.create_index("user_id")
                self.chats.create_index("created_at")
                self.chats.create_index([("user_id", 1), ("created_at", -1)])
                # 为消息数组中的字段创建索引
                self.chats.create_index("messages.timestamp")
                self.chats.create_index("messages.sender")
                
                # 绘画分析结果集合索引
                self.drawingAnalyses.create_index("user_id")
                self.drawingAnalyses.create_index("analysis_date")
                self.drawingAnalyses.create_index([("user_id", 1), ("analysis_date", -1)])
                self.drawingAnalyses.create_index("created_at")

                logging.info("数据库索引创建完成")
            except Exception as e:
                logging.warning(f"创建索引时出现警告: { str(e) }")