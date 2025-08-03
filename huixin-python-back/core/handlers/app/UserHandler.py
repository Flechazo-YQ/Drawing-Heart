import logging, flask, datetime

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.EmailCodeHandler import EmailCodeHandler

from typing import Any, Final

class UserHandler:
    ANALYSIS_TIME_CONFIG: Final[dict[str, dict[str, Any]]] = {
        'today': {
            'query': lambda userId: MongoDBConfig.drawingAnalysisManager.getRecentAnalysis(userId, hours=0),
            'desc': '今日'
        },
        '4hours': {
            'query': lambda userId: MongoDBConfig.drawingAnalysisManager.getRecentAnalysis(userId, hours=4),
            'desc': '4小时内'
        },
        'recent': {
            'query': lambda userId: (
                MongoDBConfig.drawingAnalysisManager.getRecentAnalysis(userId, hours=0)
                or MongoDBConfig.drawingAnalysisManager.getRecentAnalysis(userId, hours=4)
            ),
            'desc': '当日或4小时内'
        },
        'none': {
            'query': lambda userId: MongoDBConfig.drawingAnalysisManager.getLatestAnalysis(userId),
            'desc': ''
        }
    }

    # 登录处理
    @staticmethod
    @GlobalState.APP.route('/api/login', methods=['GET', 'POST'])
    def login():

        # 如果是GET请求, 返回登录页面
        if (flask.request.method != 'POST'):
            return flask.render_template('login.html')
        
        # 如果是POST请求, 处理登录逻辑
        data = flask.request.get_json()
        usernameOrEmail = data.get('username')
        password = data.get('password')
        
        # 先尝试用用户名查找
        user = MongoDBConfig.userManager.getUserByUsername(usernameOrEmail)

        # 如果用户名找不到, 尝试用邮箱查找
        if (not user):
            user = MongoDBConfig.userManager.getUserByEmail(usernameOrEmail)

        # 如果用户名和邮箱都找不到, 返回错误
        if (not user):
            return flask.jsonify({'code': 1, 'message': '用户名或邮箱不存在'})
        
        # 验证密码
        storedHash = user.get('password')

        if (storedHash is None or not MongoDBConfig.userManager.verifyPasswordByHash(password, storedHash)):
            return flask.jsonify({'code': 1, 'message': '密码错误'})
        
        # 如果密码正确, 生成用户令牌
        token = UserTokenHandler.generateUserToken(str(user['_id']))

        # 注意：确保返回格式符合前端预期
        return flask.jsonify({
            'code': 0, 
            'message': '登录成功', 
            'token': token,
            'data': {
                'token': token,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'avatar': user.get('avatar', '')
                }
            }
        })
    
    # 发送验证码处理
    @staticmethod
    @GlobalState.APP.route('/api/send-code', methods=['POST'])
    def sendVerificationCode():
        data = flask.request.get_json()
        email = data.get('email')

        if (not email):
            return flask.jsonify({
                'code': 1, 
                'message': '邮箱不能为空'
            }), 400

        # 检查邮箱是否已被注册
        if (MongoDBConfig.userManager.getUserByEmail(email)):
            return flask.jsonify({
                'code': 1, 
                'message': '该邮箱已被注册'
            }), 400

        code = EmailCodeHandler.sendEmailCode(email)

        # 如果验证码发送成功, 记录验证码和过期时间
        if (code):
            # 存储验证码和过期时间（例如, 10分钟后）
            EmailCodeHandler.verificationCodes[email] = {
                'code': code,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }
            logging.info(f'向 { email } 发送验证码: { code }')
            return flask.jsonify({
                'code': 0, 
                'message': '验证码已发送, 请注意查收'
            })
        

        # 如果发送失败, 记录错误并返回
        logging.error(f'向 { email } 发送验证码失败')
        return flask.jsonify({
            'code': 1, 
            'message': '验证码发送失败, 请稍后重试'
        }), 500


    # 注册处理
    @staticmethod
    @GlobalState.APP.route('/api/register', methods=['GET', 'POST'])
    def register():
        if (flask.request.method != 'POST'):
            return flask.render_template('register.html')

        data = flask.request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender')
        code = data.get('code')

        if (not all([username, password, email, gender, code])):
            return flask.jsonify({
                'code': 1, 
                'message': '所有字段均为必填项'
            })

        # 验证验证码
        storedCodeInfo = EmailCodeHandler.verificationCodes.get(email)

        if (not storedCodeInfo or storedCodeInfo['code'] != code):
            return flask.jsonify({
                'code': 1, 
                'message': '验证码错误'
            })

        if (datetime.datetime.utcnow() > storedCodeInfo['exp']):
            if email in EmailCodeHandler.verificationCodes:
                del EmailCodeHandler.verificationCodes[email]
            return flask.jsonify({
                'code': 1, 
                'message': '验证码已过期, 请重新发送'
            })

        if (MongoDBConfig.userManager.getUserByUsername(username)):
            return flask.jsonify({
                'code': 1, 
                'message': '用户名已存在'
            })

        if (MongoDBConfig.userManager.getUserByEmail(email)):
            return flask.jsonify({
                'code': 1, 
                'message': '邮箱已被注册'
            })

        # 创建用户
        MongoDBConfig.userManager.createUser(username, password, email, gender)

        # 注册成功后删除验证码
        if (email in EmailCodeHandler.verificationCodes):
            del EmailCodeHandler.verificationCodes[email]

        return flask.jsonify({
            'code': 0, 
            'message': '注册成功'
        })

    # 忘记密码处理
    @staticmethod
    @GlobalState.APP.route('/forgot', methods=['GET', 'POST'])
    def forgot():
        return flask.render_template('forgot.html')
    
    # 发送重置密码验证码处理
    @staticmethod
    @GlobalState.APP.route('/reset-password', methods=['POST'])
    def sendResetCode():
        try:
            data = flask.request.get_json()
            email = data.get('email')

            # 如果邮箱为空, 返回错误
            if (not email):
                return flask.jsonify({
                    'code': 1, 
                    'message': '邮箱不能为空'
                }), 400

            # 检查邮箱是否存在
            user = MongoDBConfig.userManager.getUserByEmail(email)

            if (not user):
                return flask.jsonify({
                    'code': 1, 
                    'message': '该邮箱未注册'
                }), 400

            code = EmailCodeHandler.sendEmailCode(email)

            # 如果验证码发送失败, 返回错误
            if (not code):
                return flask.jsonify({
                    'code': 1, 
                    'message': '验证码发送失败, 请稍后重试'
                }), 500
            
            # 存储验证码和过期时间
            EmailCodeHandler.verificationCodes[email] = {
                'code': code,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            }
            return flask.jsonify({
                'code': 0, 
                'message': '验证码已发送, 请注意查收'
            })
        except Exception as e:
            return flask.jsonify({
                'code': 1, 
                'message': f'验证码发送失败: { str(e) }'
            }), 500

    # 获取用户名, 并返回JSON格式的响应
    @staticmethod
    @GlobalState.APP.route('/getusername', methods=['GET'])
    def getUsername():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({ 'message': 'Token is missing!' }), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({ 'message': 'Invalid token!' }), 401

        try:
            # 从MongoDB获取用户信息
            user = MongoDBConfig.userManager.getUserById(userId[0])

            # 如果用户不存在, 返回404错误
            if (not user):
                return flask.jsonify({ 'message': 'User not found' }), 404

            return flask.jsonify({ 'username': user['username'] })
        except Exception as e:

            # 如果发生错误, 返回500错误和错误信息
            return flask.jsonify({ 'error': str(e) }), 500
        
    # 获取用户详细信息
    @staticmethod
    @GlobalState.APP.route('/api/user/info', methods=['GET'])
    def getUserInfo():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({ 'message': 'Token is missing!' }), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({ 'message': 'Invalid token!' }), 401

        try:
            user = MongoDBConfig.userManager.getUserById(userId[0])

            # 如果用户不存在, 返回404错误
            if (not user):
                return flask.jsonify({ 'message': 'User not found' }), 404
            
            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'chance': user.get('chance', 10),
                    'is_team': user.get('is_team', ''),
                    'avatar': user.get('avatar', ''),
                    'gender': user.get('gender', '')
                }
            })
        
        except Exception as e:
            logging.error(f'获取用户信息错误: { str(e) }')

            return flask.jsonify({ 'message': str(e) }), 500
        
    #获取用户的绘画分析历史
    @staticmethod
    @GlobalState.APP.route('/api/user/analyses', methods=['GET'])
    def getUserAnalyses():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({ 'message': 'Token is missing!' }), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({ 'message': 'Invalid token!' }), 401

        try:
            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 10))

            analyses = MongoDBConfig.drawingAnalysisManager.getUserAnalyses(userId[0], limit, page)

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'analyses': analyses,
                    'page': page,
                    'limit': limit,
                    'total': len(analyses)
                }
            })
        
        except Exception as e:
            logging.error(f'获取用户分析历史错误: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'获取分析历史失败: { str(e) }'
            }), 500
        
    # 获取用户当日的绘画分析结果
    @staticmethod
    @GlobalState.APP.route('/api/user/today-analysis', methods=['GET'])
    def getTodayAnalysis():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            todayAnalysis = MongoDBConfig.drawingAnalysisManager.getTodayAnalysis(userId[0])

            if (not todayAnalysis):
                return flask.jsonify({
                    'code': 1,
                    'message': '今日暂无分析记录'
                }), 404
            
            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': todayAnalysis
            })
        except Exception as e:
            logging.error(f'获取当日分析结果错误: { str(e) }')
            
            return flask.jsonify({
                'code': 1,
                'message': f'获取当日分析结果失败: { str(e) }'
            }), 500
        
    #获取用户最新的绘画分析结果(可选择时间限制)
    @classmethod
    @GlobalState.APP.route('/api/user/latest-analysis', methods=['GET'])
    def getLatestAnalysis(cls):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        # 获取时间限制参数, 默认为不限制时间
        timeLimit = flask.request.args.get('time_limit', 'none')  # none, today, 4hours
        config = cls.ANALYSIS_TIME_CONFIG.get(timeLimit, cls.ANALYSIS_TIME_CONFIG['none'])

        try:
            latestAnalysis = config['query'](userId[0])

            if (not latestAnalysis):

                # 如果没有找到分析结果, 返回相应的消息
                timeDesc = config['desc']

                return flask.jsonify({
                    'code': 1,
                    'message': f'暂无{ timeDesc }分析记录'
                }), 404
            
            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': latestAnalysis
            })
            
        except Exception as e:
            logging.error(f'获取最新分析结果错误: { str(e) }')

            return flask.jsonify({
                'code': 1,
                'message': f'获取最新分析结果失败: { str(e) }'
            }), 500
