import logging, flask, mongodb_config

from states.TokenState import TokenState
from states.GlobalState import GlobalState
from handlers.token.UserTokenHandler import UserTokenHandler

from mongodb_config import user_manager, drawing_analysis_manager

class UserHandler:

    # 登录处理
    @staticmethod
    @GlobalState.app.route('/login', methods=['GET', 'POST'])
    def login():
        if (flask.request.method == 'POST'):
            data = flask.request.get_json()
            username_or_email = data.get('username')  # 前端传来的可能是用户名或邮箱
            password = data.get('password')
            
            try:
                # 先尝试按邮箱查找
                user = user_manager.get_user_by_email(username_or_email)
                
                # 如果按邮箱没找到，尝试按用户名查找
                if (not user):
                    # 由于MongoDB中没有直接按用户名查找的方法，需要扩展
                    from mongodb_config import mongodb
                    user = mongodb.users.find_one({
                        "$or": [
                            {"username": username_or_email},
                            {"email": username_or_email}
                        ],
                        "is_active": True
                    })

                if (user and user['password'] == TokenState.sha256Hash(password)):
                    token = UserTokenHandler.generateUserToken([str(user['_id']), user['username']])

                    return flask.jsonify({
                        'code': 0,
                        'message': '登录成功',
                        'data': {
                            'token': token,
                            'user': {
                                'id': str(user['_id']),
                                'username': user['username'],
                                'email': user['email'],
                                'avatar': user.get('avatar', ''),
                                'chance': user.get('chance', 10)
                            }
                        }
                    }), 200
                else:
                    return flask.jsonify({
                        'code': 1,
                        'message': '用户名/邮箱或密码错误'
                    }), 401
            except Exception as e:
                logging.error(f"登录错误: { str(e) }")

                return flask.jsonify({
                    'code': 1,
                    'message': '登录失败，请稍后重试'
                }), 500
            
        return flask.render_template('login.html')
    
    # 注册处理
    @staticmethod
    @GlobalState.app.route('/register', methods=['GET', 'POST'])
    def register():
        if (flask.request.method == 'POST'):
            try:
                data = flask.request.get_json()
                username = data.get('username')
                password = data.get('password')
                email = data.get('email')
                gender = data.get('gender')

                if not all([username, password, email, gender]):
                    return flask.jsonify({
                        'code': 1,
                        'message': '请填写所有必需的字段'
                    }), 400

                # 检查邮箱是否已存在
                existingUser = user_manager.get_user_by_email(email)

                if (existingUser):
                    return flask.jsonify({
                        'code': 1,
                        'message': '邮箱已被注册'
                    }), 400
                
                # 检查用户名是否已存在
                existingUsername = mongodb_config.mongodb.users.find_one({ "username": username, "is_active": True })

                if (existingUsername):
                    return flask.jsonify({
                        'code': 1,
                        'message': '用户名已存在'
                    }), 400

                # 创建新用户
                user_id = user_manager.create_user(
                    username=username,
                    email=email,
                    password=TokenState.sha256Hash(password),
                    gender=gender,
                    chance=5,
                    is_team='false'
                )

                return flask.jsonify({
                    'code': 0,
                    'message': '注册成功'
                }), 200
                    
            except Exception as e:
                logging.error(f"注册错误: { str(e) }")

                return flask.jsonify({
                    'code': 1,
                    'message': '注册失败，请稍后重试'
                }), 500

        return flask.render_template('register.html')
    
    # 忘记密码处理
    @staticmethod
    @GlobalState.app.route('/forgot', methods=['GET', 'POST'])
    def forgot():
        return flask.render_template('forgot.html')
    
    # 获取用户名
    @staticmethod
    @GlobalState.app.route('/getusername', methods=['GET'])
    def getUsername():

        """
        处理获取用户名的请求, 并返回JSON格式的响应。
        """
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            # 从MongoDB获取用户信息
            user = user_manager.get_user_by_id(userId[0])

            if (user):
                return flask.jsonify({ 'username': user['username'] })
            else:
                return flask.jsonify({ 'message': 'User not found' }), 404
        except Exception as e:
            # 如果发生错误，返回500错误和错误信息
            return flask.jsonify({ 'error': str(e) }), 500
        
    # 获取用户详细信息
    @staticmethod
    @GlobalState.app.route('/api/user/info', methods=['GET'])
    def getUserInfo():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({ 'message': 'Token is missing!' }), 401
        
        user_id = UserTokenHandler.verifyUserToken(token)

        if (not user_id):
            return flask.jsonify({ 'message': 'Invalid token!' }), 401

        try:
            user = user_manager.get_user_by_id(user_id[0])

            if (user):
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
            return flask.jsonify({'message': 'User not found'}), 404
        
        except Exception as e:
            logging.error(f"获取用户信息错误: { str(e) }")

            return flask.jsonify({ 'message': str(e) }), 500
        
    #获取用户的绘画分析历史
    @staticmethod
    @GlobalState.app.route('/api/user/analyses', methods=['GET'])
    def getUserAnalyses():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            page = int(flask.request.args.get('page', 1))
            limit = int(flask.request.args.get('limit', 10))

            analyses = drawing_analysis_manager.get_user_analyses(userId[0], limit, page)

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
            logging.error(f"获取用户分析历史错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取分析历史失败: { str(e) }'
            }), 500
        
    # 获取用户当日的绘画分析结果
    @staticmethod
    @GlobalState.app.route('/api/user/today-analysis', methods=['GET'])
    def getTodayAnalysis():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        try:
            todayAnalysis = drawing_analysis_manager.get_today_analysis(userId[0])

            if (todayAnalysis):
                return flask.jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': todayAnalysis
                })
            else:
                return flask.jsonify({
                    'code': 1,
                    'message': '今日暂无分析记录'
                }), 404
        except Exception as e:
            logging.error(f"获取当日分析结果错误: { str(e) }")
            return flask.jsonify({
                'code': 1,
                'message': f'获取当日分析结果失败: { str(e) }'
            }), 500
        
    #获取用户最新的绘画分析结果(可选择时间限制)
    @staticmethod
    @GlobalState.app.route('/api/user/latest-analysis', methods=['GET'])
    def getLatestAnalysis():
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401

        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401

        # 获取时间限制参数，默认为不限制时间
        timeLimit = flask.request.args.get('time_limit', 'none')  # none, today, 4hours

        try:
            latestAnalysis = None

            if (timeLimit == 'today'):

                # 获取当日分析结果
                latestAnalysis = drawing_analysis_manager.get_recent_analysis(userId[0], hours=0)
            elif (timeLimit == '4hours'):

                # 获取4小时内分析结果
                latestAnalysis = drawing_analysis_manager.get_recent_analysis(userId[0], hours=4)
            elif (timeLimit == 'recent'):

                # 获取当日或4小时内的分析结果（优先当日）
                latestAnalysis = drawing_analysis_manager.get_recent_analysis(userId[0], hours=0)
                if not latestAnalysis:
                    latestAnalysis = drawing_analysis_manager.get_recent_analysis(userId[0], hours=4)
            else:

                # 默认获取最新分析结果（不限时间）
                latestAnalysis = drawing_analysis_manager.get_latest_analysis(userId[0])

            if (latestAnalysis):
                return flask.jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': latestAnalysis
                })
            else:
                timeDesc = ""

                if (timeLimit == 'today'):
                    timeDesc = "今日"
                elif (timeLimit == '4hours'):
                    timeDesc = "4小时内"
                elif (timeLimit == 'recent'):
                    timeDesc = "当日或4小时内"
                else:
                    timeDesc = ""

                return flask.jsonify({
                    'code': 1,
                    'message': f'暂无{ timeDesc }分析记录'
                }), 404
            
        except Exception as e:
            logging.error(f"获取最新分析结果错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f'获取最新分析结果失败: { str(e) }'
            }), 500