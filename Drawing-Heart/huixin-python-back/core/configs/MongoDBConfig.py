import logging

from pymongo import MongoClient

class MongoDBConfig:

    @classmethod
    def init(cls, connectionString="mongodb://localhost:27017/", databaseName="HuixinDB"):
        from core.managers.UserManager import UserManager
        from core.managers.ChatManager import ChatManager
        from core.managers.MessageManager import MessageManager
        from core.managers.DrawingManager import DrawingManager
        from core.managers.AdminManager import AdminManager
        from core.managers.CodeManager import CodeManager

        cls.mongoDb = cls.MongoDB(connectionString, databaseName)
        cls.userManager = UserManager(cls.mongoDb)
        cls.chatManager = ChatManager(cls.mongoDb)
        cls.messageManager = MessageManager(cls.mongoDb)
        cls.drawingManager = DrawingManager(cls.mongoDb)
        cls.adminManager = AdminManager(cls.mongoDb)
        cls.codeManager = CodeManager(cls.mongoDb)

        logging.info("✅ MongoDB初始化完成")
        return cls.mongoDb

    class MongoDB:

        # 初始化MongoDB连接
        def __init__(self, connectionString="mongodb://localhost:27017/", databaseName="HuixinDB"):
            try:
                self.client = MongoClient(connectionString)
                self.db = self.client[databaseName]

                # 测试连接
                self.client.server_info()
                logging.info(f"✅ 成功连接到MongoDB数据库: { databaseName }")
            except Exception as e:
                logging.error(f"❌ 连接MongoDB失败: { str(e) }")
                raise e
            
            # 获取集合
            self.users = self.db.users
            self.chats = self.db.chats
            self.messages = self.db.messages
            self.drawings = self.db.drawings
            self.admins = self.db.admins
            self.codes = self.db.codes

            # 创建索引
            self.createIndexes()

        # 创建索引以优化查询性能
        def createIndexes(self):
            try:
                # 管理员集合索引
                self.admins.create_index("name", unique=True)

                # 用户集合索引
                self.users.create_index("email", unique=True)
                self.users.create_index("name")
                
                # 对话集合索引
                self.chats.create_index("userId")
                self.chats.create_index("timeNode.createdAt")
                self.chats.create_index([("userId", 1), ("timeNode.createdAt", -1)])

                # 为消息数组中的字段创建索引
                self.chats.create_index("messages.timestamp")
                self.chats.create_index("messages.sender")
                
                # 绘画分析结果集合索引
                self.drawings.create_index("userId")
                self.drawings.create_index("analysisDate")
                self.drawings.create_index([("userId", 1), ("analysisDate", -1)])
                self.drawings.create_index("createdAt")

                logging.info("✅ 数据库索引创建完成")
            except Exception as e:
                logging.warning(f"⚠️ 创建索引时出现警告: { str(e) }")