import flask, logging

from core.configs.BlueprintConfig import BlueprintConfig
from core.configs.MongoDBConfig import MongoDBConfig
from core.states.route.ApiState import ApiState
from core.utils.token.UserTokenHelper import UserTokenHelper 

from datetime import datetime

class UserAnalysisHandler:

    #获取用户的绘画分析历史
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.ANALYSES_HISTORY['route'], methods=ApiState.ANALYSES_HISTORY['method'])
    @UserTokenHelper.userTokenRequired
    def getHistory():
        try:
            user = flask.g.user
            page = int(flask.request.args.get("page", 1))
            limit = int(flask.request.args.get("limit", 10))

            (analyses, total) = MongoDBConfig.drawingManager.getAnalysesHistory(user["_id"], limit, page)

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
    @BlueprintConfig.apiRoutes(ApiState.ANALYSES_TODAY['route'], methods=ApiState.ANALYSES_TODAY['method'])
    @UserTokenHelper.userTokenRequired
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
            logging.error(f"❌ 获取当日分析结果错误: { str(e) }")
            
            return flask.jsonify({
                "code": 1,
                "message": f"获取当日分析结果失败: { str(e) }"
            }), 500
        
    #获取用户最新的绘画分析结果(可选择时间限制)
    @staticmethod
    @BlueprintConfig.apiRoutes(ApiState.ANALYSES_LATEST['route'], methods=ApiState.ANALYSES_LATEST['method'])
    @UserTokenHelper.userTokenRequired
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
        
    @staticmethod
    def getByTime():
        try:
            user = flask.g.user
            userId = str(user["_id"])

            start = flask.request.args.get("start")
            end = flask.request.args.get("end")

            if (not start or not end):
                return flask.jsonify({
                    'code': 1,
                    'message': '时间范围参数不完整'
                })

            start = datetime.fromisoformat(start)
            end = datetime.fromisoformat(end)

            if (not start or not end):
                return flask.jsonify({
                    'code': 1,
                    'message': '时间范围参数无效'
                })

            (analyses, total) = MongoDBConfig.drawingManager.getAnalysisByDateRange(userId, start, end)

            return flask.jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'analyses': analyses,
                    'total': total
                }
            })

        except Exception as e:
            logging.error(f"❌ 获取指定时间范围内分析结果错误: { str(e) }")

            return flask.jsonify({
                'code': 1,
                'message': f"获取指定时间范围内分析结果失败: { str(e) }"
            }), 500