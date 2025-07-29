import flask

class GlobalState:
    userLatestImages = {} #存储用户的最新图片URL
    userContexts = {} #存储每个用户的上下文，避免全局变量混乱
    userConnections = {} #存储用户连接
    userCurrentChats = {} #存储用户当前活跃聊天ID

    #存储危险对话
    dangerousChats = {}
    activeAdmins = {}

    url = "https://api.siliconflow.cn/v1/chat/completions"

    #允许的文件扩展名
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    #保存图片的目录
    SAVE_DIR = "saved_drawings"

    app = flask.Flask(__name__)