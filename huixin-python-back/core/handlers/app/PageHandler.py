import flask, datetime

from core.states.GlobalState import GlobalState

from flask import Response

class PageHandler:

    # 返回主页的HTML内容
    @staticmethod
    @GlobalState.APP.route('/')
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
                '心理对话': '/api/stream-chat',
                '用户信息': '/api/user/info',
                '发送验证码': '/api/send-code'
            }
        })

    # 返回绘图页面的HTML内容
    @staticmethod
    @GlobalState.APP.route('/draw')
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
    @GlobalState.APP.route('/analyse')
    def analyse():
        return flask.render_template('index.html')

    # 返回隐私页面的HTML内容
    @staticmethod
    @GlobalState.APP.route('/privacy')
    def privacy():

        # 由于前端已经有Vue路由处理/privacy，我们应该返回前端应用
        return flask.render_template('index.html')  # 返回前端入口文件
    
    # 返回聊天页面的HTML内容
    @staticmethod
    @GlobalState.APP.route('/chat', methods=['GET'])
    def chat():
        return flask.render_template('chat.html')
    
    # 返回静态文件
    @staticmethod
    @GlobalState.APP.route('/templates/<filename>')
    def getFile(filename):
        return flask.send_from_directory('templates', filename)