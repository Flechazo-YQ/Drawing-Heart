import logging, flask

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.handlers.EmailCodeHandler import EmailCodeHandler
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.utils.PasswordHelper import PasswordHelper
from core.utils.UrlHelper import UrlHelper

from typing import Any, Final, Dict, Callable

class UserHandler:
    class Code:

        # 发送注册验证码处理
        @staticmethod
        @BlueprintConfig.apiRoutes("/code/register", methods=["POST"])
        def sendRegisterCode():
            data = flask.request.get_json()
            email = data.get("email")

            if (not email):
                return flask.jsonify({
                    "code": 1, 
                    "message": "邮箱不能为空"
                }), 400

            # 检查邮箱是否已被注册
            if (MongoDBConfig.userManager.getUserByEmail(email)):
                return flask.jsonify({
                    "code": 1, 
                    "message": "该邮箱已被注册"
                }), 400

            code = MongoDBConfig.verificationCodeManager.createCode(email, "registry")

            if (not code or not EmailCodeHandler.sendEmailCode(email)):
                logging.error(f"❌ 向 { email } 发送验证码失败")
                return flask.jsonify({
                    "code": 1,
                    "message": "验证码发送失败, 请稍后重试"
                }), 500

            logging.info(f"向 { email } 发送验证码成功")
            return flask.jsonify({
                "code": 0,
                "message": "验证码已发送, 请注意查收"
            })

        # 发送重置密码验证码处理
        @staticmethod
        @BlueprintConfig.apiRoutes("/code/reset", methods=["POST"])
        def sendResetPasswordCode():
            data = flask.request.get_json()
            email = data.get("email")

            if (not email):
                return flask.jsonify({
                    "code": 1,
                    "message": "邮箱不能为空"
                }), 400
            
            if (not MongoDBConfig.userManager.getUserByEmail(email)):
                return flask.jsonify({
                    "code": 1,
                    "message": "该邮箱未注册"
                }), 400

            code = MongoDBConfig.verificationCodeManager.createCode(email, "resetPassword")

            if (not code or not EmailCodeHandler.sendEmailCode(email)):
                logging.error(f"❌ 向 { email } 发送验证码失败")
                return flask.jsonify({
                    "code": 1,
                    "message": "验证码发送失败, 请稍后重试"
                }), 500
            
            logging.info(f"向 { email } 发送重置密码验证码: { code }")
            return flask.jsonify({
                "code": 0,
                "message": "验证码已发送, 请注意查收"
            })

    class Analysis:
        ANALYSIS_QUERY = Callable[[str], Any]
        ANALYSIS_TIME_CONFIG: Final[Dict[str, Dict[str, ANALYSIS_QUERY | str]]] = {
            "today": {
                "query": lambda userId: MongoDBConfig.drawingManager.getRecentAnalysis(userId, hours=0),
                "desc": "今日"
            },
            "4hours": {
                "query": lambda userId: MongoDBConfig.drawingManager.getRecentAnalysis(userId, hours=4),
                "desc": "4小时内"
            },
            "recent": {
                "query": lambda userId: (
                    MongoDBConfig.drawingManager.getRecentAnalysis(userId, hours=0)
                    or MongoDBConfig.drawingManager.getRecentAnalysis(userId, hours=4)
                ),
                "desc": "当日或4小时内"
            },
            "none": {
                "query": lambda userId: MongoDBConfig.drawingManager.getLatestAnalysis(userId),
                "desc": ""
            }
        }

        #获取用户的绘画分析历史
        @staticmethod
        @BlueprintConfig.apiRoutes("/analyses", methods=["GET"])
        @UserTokenHandler.userTokenRequired
        def getHistory():
            try:
                user = flask.g.user
                page = int(flask.request.args.get("page", 1))
                limit = int(flask.request.args.get("limit", 10))

                (analyses, total) = MongoDBConfig.drawingManager.getUserAnalyses(user["_id"], limit, page)

                return flask.jsonify({
                    "code": 0,
                    "message": "success",
                    "data": {
                        "analyses": analyses,
                        "page": page,
                        "limit": limit,
                        "total": total
                    }
                })

            except Exception as e:
                logging.error(f"❌ 获取用户分析历史错误: { str(e) }")

                return flask.jsonify({
                    "code": 1,
                    "message": f"获取分析历史失败: { str(e) }"
                }), 500

        # 获取用户当日的绘画分析结果
        @staticmethod
        @BlueprintConfig.apiRoutes("/analyses/today", methods=["GET"])
        @UserTokenHandler.userTokenRequired
        def getToday():
            try:
                user = flask.g.user
                todayAnalysis = MongoDBConfig.drawingManager.getTodayAnalysis(str(user["_id"]))

                if (not todayAnalysis):
                    return flask.jsonify({
                        "code": 1,
                        "message": "今日暂无分析记录"
                    }), 404
                
                return flask.jsonify({
                    "code": 0,
                    "message": "success",
                    "data": todayAnalysis
                })
            except Exception as e:
                logging.error(f"获取当日分析结果错误: { str(e) }")
                
                return flask.jsonify({
                    "code": 1,
                    "message": f"获取当日分析结果失败: { str(e) }"
                }), 500
            
        #获取用户最新的绘画分析结果(可选择时间限制)
        @staticmethod
        @BlueprintConfig.apiRoutes("/analyses/latest", methods=["GET"])
        @UserTokenHandler.userTokenRequired
        def getLatest():
            try:
                user = flask.g.user
                analysis = MongoDBConfig.drawingManager.getLatestAnalysis(str(user["_id"]))

                if (not analysis):
                    return flask.jsonify({
                        "code": 1,
                        "message": "暂无分析记录"
                    }), 404

                return flask.jsonify({
                    "code": 0,
                    "message": "success",
                    "data": analysis
                })

            except Exception as e:
                logging.error(f"❌ 获取最新分析结果错误: { str(e) }")

                return flask.jsonify({
                    "code": 1,
                    "message": f"获取最新分析结果失败: { str(e) }"
                }), 500
            
    class Auth:
        
        # 登录处理
        @staticmethod
        @BlueprintConfig.apiRoutes("/login", methods=["POST"])
        def login():
            data = flask.request.get_json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            user = MongoDBConfig.userManager.getUserByUsername(username) or MongoDBConfig.userManager.getUserByEmail(email)

            # 如果用户名和邮箱都找不到, 返回错误
            if (not user):
                return flask.jsonify({
                    "code": 1, 
                    "message": "用户名或邮箱不存在"
                })

            # 验证密码
            storedHash = user.get("password", "")

            if (storedHash is None or not PasswordHelper.verifyHashPassword(password, storedHash)):
                return flask.jsonify({
                    "code": 1, 
                    "message": "密码错误"
                })
            
            # 如果密码正确, 生成用户令牌
            token = UserTokenHandler.generateUserToken(str(user["_id"]))

            # 注意：确保返回格式符合前端预期
            return flask.jsonify({
                "code": 0, 
                "message": "登录成功", 
                "token": token,
                "user": {
                    "id": str(user["_id"]),
                    "username": user["name"],
                    "email": user["email"],
                    "avatar": user.get("profile", {}).get("avatar", "")
                }
            })
        
        # 注册处理
        @staticmethod
        @BlueprintConfig.apiRoutes("/register", methods=["GET", "POST"])
        def register():
            if (flask.request.method != "POST"):
                return flask.render_template("register.html")

            data = flask.request.get_json()
            username = data.get("username")
            password = data.get("password")
            email = data.get("email")
            gender = data.get("gender")
            code = data.get("code")

            if (not all([username, password, email, gender, code])):
                return flask.jsonify({
                    "code": 1, 
                    "message": "所有字段均为必填项"
                }), 400

            if (not MongoDBConfig.verificationCodeManager.verifyCode(email, code, "register")):
                return flask.jsonify({
                    "code": 1, 
                    "message": "验证码错误或已过期"
                }), 400
            
            if (MongoDBConfig.userManager.getUserByUsername(username)):
                return flask.jsonify({
                    "code": 1, 
                    "message": "用户名已存在"
                }), 409

            if (MongoDBConfig.userManager.getUserByEmail(email)):
                return flask.jsonify({
                    "code": 1, 
                    "message": "邮箱已被注册"
                }), 409

            userId = MongoDBConfig.userManager.createUser(username, password, email, gender)

            if (not userId):
                return flask.jsonify({
                    "code": 1, 
                    "message": "注册失败, 请稍后重试"
                }), 500

            return flask.jsonify({
                "code": 0, 
                "message": "注册成功"
            }), 201

        # 忘记密码处理
        @staticmethod
        @BlueprintConfig.apiRoutes("/forgot", methods=["GET", "POST"])
        def forgot():
            return flask.render_template("forgot.html")
        
    class Profile:

        # 获取用户名, 并返回JSON格式的响应
        @staticmethod
        @BlueprintConfig.apiRoutes("/name", methods=["GET"])
        @UserTokenHandler.userTokenRequired
        def getUsername():
            user = flask.g.user

            return flask.jsonify({
                "username": user["name"]
            })

        # 获取用户详细信息
        @staticmethod
        @BlueprintConfig.apiRoutes("/info", methods=["GET"])
        @UserTokenHandler.userTokenRequired
        def getUserInfo():
            try:
                user = flask.g.user
                logging.info(f"获取用户信息: { user }")
                profile = user.get("profile", {})
                avatarUrl = UrlHelper.getAbsoluteUrl(profile.get("avatar", ""))
                profile["avatar"] = avatarUrl
                user["profile"] = profile

                return flask.jsonify({
                    "code": 0,
                    "message": "success",
                    "data": user
                })
            except Exception as e:
                return flask.jsonify({
                    "error": str(e)
                }), 500
            
