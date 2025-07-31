import flask

from states.GlobalState import GlobalState

from flask import Response

class PageHandler:

    # 返回主页的HTML内容
    @staticmethod
    @GlobalState.app.route('/')
    def index():
        try:
            with open('templates/Home.html', 'r', encoding='utf-8') as file:
                html_content = file.read()

                # 返回HTML内容作为响应
            return Response(html_content, mimetype='text/html')
        
        except FileNotFoundError:

            # 如果文件不存在，返回404错误
            return 'File not found', 404

    # 返回绘图页面的HTML内容
    @staticmethod
    @GlobalState.app.route('/draw')
    def draw():
        try:
            with open('templates/draw.html', 'r', encoding='utf-8') as file:
                html_content = file.read()

                # 返回HTML内容作为响应
            return Response(html_content, mimetype='text/html')
        
        except FileNotFoundError:

            # 如果文件不存在，返回404错误
            return 'File not found', 404
        
    # 返回分析页面的HTML内容
    @staticmethod
    @GlobalState.app.route('/analyse')
    def analyse():
        return flask.render_template('index.html')

    # 返回隐私页面的HTML内容
    @staticmethod
    @GlobalState.app.route('/privacy')
    def privacy():

        # 由于前端已经有Vue路由处理/privacy，我们应该返回前端应用
        return flask.render_template('index.html')  # 返回前端入口文件
    
    # 返回聊天页面的HTML内容
    @staticmethod
    @GlobalState.app.route('/chat', methods=['GET'])
    def chat():
        return flask.render_template('chat.html')
    
    # 返回静态文件
    @staticmethod
    @GlobalState.app.route('/templates/<filename>')
    def getFile(filename):
        return flask.send_from_directory('templates', filename)