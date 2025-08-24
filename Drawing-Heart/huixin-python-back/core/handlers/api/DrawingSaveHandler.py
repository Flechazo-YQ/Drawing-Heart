import os, logging, flask, time

from core.configs.BlueprintConfig import BlueprintConfig
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.DrawingHandler import DrawingHandler
from core.states.DirectoryState import DirectoryState
from core.utils.ImageHelper import ImageHelper

class DrawingSaveHandler:
    
    # 保存绘画并可选进行分析
    @staticmethod
    @BlueprintConfig.apiRoutes('/save', methods=['POST'])
    @UserTokenHandler.userTokenRequired
    def saveDrawing():
        try:
            user = flask.g.user
            data = flask.request.get_json()

            if (not data):
                return flask.jsonify({
                    "code": 1,
                    "message": "无效的请求数据"
                }), 400

            image = data.get("image")

            if (not image):
                return flask.jsonify({
                    "code": 1,
                    "message": "无效的图像数据"
                }), 400

            imageBytes = ImageHelper.decodeBase64Image(image)

            if (not imageBytes or len(imageBytes) < 100):
                return flask.jsonify({
                    "code": 1,
                    "message": "无效或损坏的图像数据"
                }), 400

            userId = str(user["_id"])
            timestamp = int(time.time() * 1000)
            userDir = os.path.join(DirectoryState.SAVE_DIR, userId)

            os.makedirs(userDir, exist_ok=True)

            fileName = f"{ timestamp }.png"
            filePath = os.path.join(userDir, fileName)

            with open(filePath, "wb") as f:
                f.write(imageBytes)

            logging.info(f"绘画已保存: { filePath }")

            if (data.get("analyze")):
                return DrawingHandler.analyzeImage(filePath, fileName, userId)

            return flask.jsonify({
                "code": 0,
                "message": "绘画保存成功",
                "filePath": filePath,
                "fileName": fileName
            }), 200

        except Exception as e:
            logging.error(f"❌ 绘画保存失败: { str(e) }")
            return flask.jsonify({
                "code": 1,
                "message": "绘画保存失败"
            }), 500
