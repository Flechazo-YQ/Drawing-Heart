import flask, datetime

from core.configs.BlueprintConfig import BlueprintConfig
from core.states.RouteState import RouteState

from flask import Response

class PageHandler:

    # 返回根路径的API状态信息
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.ROOT['route'])
    def root():
        return flask.jsonify({
            'status': 'success',
            'message': '绘心同学后端API服务正在运行',
            'version': '1.0.0',
            'timestamp': datetime.datetime.now().isoformat(),
            'endpoints': {
                '登录': '/api/login',
                '注册': '/api/register', 
                '绘画分析': '/api/save',
                '心理对话': '/api/chats/stream',
                '用户信息': '/api/info',
                '发送验证码': '/api/code/send'
            }
        })

    # 返回主页的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.INDEX['route'])
    def index():
        return flask.jsonify({
            'status': 'success',
            'message': '绘心同学后端API服务正在运行',
            'version': '1.0.0',
            'timestamp': datetime.datetime.now().isoformat(),
            'endpoints': {
                '登录': '/api/login',
                '注册': '/api/register', 
                '绘画分析': '/api/save',
                '心理对话': '/api/chats/stream',
                '用户信息': '/api/info',
                '发送验证码': '/api/code/send'
            }
        })

    # 返回注册页面的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.REGISTER['route'], methods=RouteState.Page.REGISTER['method'])
    def register():
        return flask.render_template("register.html")

    # 返回找回密码页面的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.FORGOT['route'], methods=RouteState.Page.FORGOT['method'])
    def forgot():
        return flask.render_template("forgot.html")

    # 返回绘图页面的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.DRAW['route'])
    def draw():
        try:
            with open('templates/draw.html', 'r', encoding='utf-8') as file:
                htmlContent = file.read()

                # 返回HTML内容作为响应
            return Response(htmlContent, mimetype='text/html')

        except FileNotFoundError:

            # 如果文件不存在，返回404错误
            return 'File not found', 404
        
    # 返回分析页面的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.ANALYSE['route'])
    def analyse():
        return flask.render_template('index.html')

    # 返回隐私页面的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.PRIVACY['route'])
    def privacy():

        # 由于前端已经有Vue路由处理/privacy，我们应该返回前端应用
        return flask.render_template('index.html')  # 返回前端入口文件
    
    # 返回聊天页面的HTML内容
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.CHAT['route'], methods=RouteState.Page.CHAT['method'])
    def chat():
        return flask.render_template('chat.html')
    
    # 返回静态文件
    @staticmethod
    @BlueprintConfig.pageRoutes(RouteState.Page.TEMPLATES_FILE['route'])
    def getFile(filename: str):
        return flask.send_from_directory('templates', filename)
