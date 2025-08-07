import os, logging, flask, re, base64

from core.configs.BlueprintConfig import BlueprintConfig
from core.handlers.token.UserTokenHandler import UserTokenHandler
from core.handlers.DrawingHandler import DrawingHandler
from core.states.GlobalState import GlobalState

from flask import jsonify

class DrawingSaveHandler:
    
    # 保存绘画并可选进行分析
    @staticmethod
    @BlueprintConfig.apiRoutes('/save', methods=['POST'])
    def saveDrawing():
        token = flask.request.headers.get('Authorization')
        
        if (not token):
            return jsonify({
                'message': 'Token is missing!'
            }), 401
            
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return jsonify({
                'message': 'Invalid token!'
            }), 401
            
        try:
            data = flask.request.json

            if (not data):
                return jsonify({
                    'message': '没有接收到数据'
                }), 400
                
            imageData = data.get('image', '')
            isUploaded = data.get('isUploaded', False)

            if (not imageData):
                return jsonify({
                    'message': '未接收到图像数据'
                }), 400

            try:
                # 处理 Base64 数据
                logging.info(f"Processing image data, size: { len(imageData) } characters")
                
                if ('base64,' in imageData):
                    header, imageData = imageData.split('base64,', 1)
                    logging.info(f"Extracted base64 data from header: { header[:50] } ...")

                # 清理Base64字符串，移除任何非base64字符
                originalLength = len(imageData)
                imageData = re.sub(r'[^A-Za-z0-9+/=]', '', imageData)

                if (len(imageData) != originalLength):
                    logging.info(f"Cleaned base64 string, removed { originalLength - len(imageData) } invalid characters")
                
                # 补充缺失的填充
                missingPadding = len(imageData) % 4

                if (missingPadding):
                    padding = '=' * (4 - missingPadding)
                    imageData += padding
                    logging.info(f"Added { len(padding) } padding characters")

                # 解码 Base64 数据
                try:
                    imageBytes = base64.b64decode(imageData)
                    logging.info(f"Successfully decoded base64 data to { len(imageBytes) } bytes")
                except Exception as decodeError:
                    logging.error(f"Base64 decode failed: { str(decodeError) }")
                    return jsonify({
                        'message': f'图像数据解码失败: { str(decodeError) }'
                    }), 400

                # 验证图像数据
                if (len(imageBytes) < 100):  # 太小的文件可能不是有效图像
                    logging.error(f"Image data too small: { len(imageBytes) } bytes")
                    return jsonify({'message': '图像数据太小，可能无效'}), 400
                
                # 生成文件名和保存图片
                fileName = f"drawing_{ len(os.listdir(GlobalState.SAVE_DIR)) + 1 }.png"
                filePath = os.path.join(GlobalState.SAVE_DIR, fileName)
                
                # 保存文件
                with open(filePath, 'wb') as f:
                    f.write(imageBytes)

                logging.info(f"Image saved successfully: { filePath }")

                # 保存用户最新的图片URL
                GlobalState.userLatestImages[str(userId[0])] = filePath
                
                # 如果是分析请求，则进行AI分析
                shouldAnalyze = data.get('analyze', False)

                if (shouldAnalyze):
                    logging.info(f"Starting analysis for image: { fileName }")
                    try:
                        return DrawingHandler.analyzeImage(filePath, fileName, userId[0])  # 传递用户ID
                    except Exception as analysisError:
                        logging.error(f"Analysis failed for { fileName }: { str(analysisError) }")
                        # 即使分析失败，图片已经保存成功，返回文件信息
                        return jsonify({
                            'message': f'图片保存成功，但分析失败: { str(analysisError) }',
                            'file_name': fileName,
                            'error': str(analysisError)
                        }), 200  # 使用200状态码，因为保存成功了
                    
                # 否则只返回保存成功的消息
                return jsonify({
                    'message': '图像保存成功',
                    'file_name': fileName
                }), 200
                    
            except Exception as e:
                logging.error(f"Image processing error: { str(e) }")
                return jsonify({'message': f'图像处理失败: { str(e) }'}), 400

        except Exception as e:
            print(f"General error: { str(e) }")
            return jsonify({'message': f'保存失败: { str(e) }'}), 500
