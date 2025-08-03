import base64, os, logging, flask, httpx, re

from core.configs.MongoDBConfig import MongoDBConfig
from core.states.GlobalState import GlobalState
from core.handlers.token.UserTokenHandler import UserTokenHandler

from openai import OpenAI
from typing import Final

class DrawingHandler:
    MIME_TYPE_CONFIG: Final[dict[str, str]] = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }

    # 文件类型校验
    @staticmethod
    def allowedFile(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in GlobalState.ALLOWED_EXTENSIONS

    # 将图片文件转换为 data URL
    @classmethod
    def imageToDataUrl(cls, filePath: str):

        # 将图片文件转换为 data URL
        try:
            extension = os.path.splitext(filePath)[1].lower()
            mimeType = cls.MIME_TYPE_CONFIG.get(extension)

            # 读取文件并转换为 base64
            with open(filePath, 'rb') as imageFile:
                encodedImage = base64.b64encode(imageFile.read()).decode('utf-8')

            # 返回完整的 data URL
            return f'data:{ mimeType };base64,{ encodedImage }'

        except Exception as e:
            print(f'Error converting image to data URL: { str(e) }')
            return None
        
    # 保存图片
    @classmethod
    @GlobalState.APP.route('/save', methods=['POST'])
    def saveDrawing(cls):
        token = flask.request.headers.get('Authorization')

        if (not token):
            return flask.jsonify({'message': 'Token is missing!'}), 401
        
        userId = UserTokenHandler.verifyUserToken(token)

        if (not userId):
            return flask.jsonify({'message': 'Invalid token!'}), 401
            
        try:
            data = flask.request.get_json()

            if (not data):
                return flask.jsonify({'message': '没有接收到数据'}), 400

            imageData = data.get('image', '')

            if (not imageData):
                return flask.jsonify({'message': '未接收到图像数据'}), 400
                
            try:
                # 处理 Base64 数据
                logging.info(f"Processing image data, size: { len(imageData) } characters")

                if ('base64,' in imageData):
                    header, imageData = imageData.split('base64,', 1)
                    logging.info(f"Extracted base64 data from header: { header[:50] }...")
                
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

                    return flask.jsonify({'message': f'图像数据解码失败: { str(decodeError) }'}), 400

                # 验证图像数据
                if (len(imageBytes) < 100):  # 太小的文件可能不是有效图像
                    logging.error(f"Image data too small: { len(imageBytes) } bytes")

                    return flask.jsonify({'message': '图像数据太小，可能无效'}), 400

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
                        return cls.analyzeImage(filePath, fileName, userId[0])  # 传递用户ID
                    
                    except Exception as analysisError:
                        logging.error(f"Analysis failed for { fileName }: { str(analysisError) }")
                        # 即使分析失败，图片已经保存成功，返回文件信息
                        return flask.jsonify({
                            'message': f'图片保存成功，但分析失败: { str(analysisError) }',
                            'file_name': fileName,
                            'error': str(analysisError)
                        }), 200  # 使用200状态码，因为保存成功了
                    
                # 否则只返回保存成功的消息
                return flask.jsonify({
                    'message': '图像保存成功',
                    'file_name': fileName
                }), 200
                    
            except Exception as e:
                logging.error(f"Image processing error: { str(e) }")
                return flask.jsonify({'message': f'图像处理失败: { str(e) }'}), 400

        except Exception as e:
            print(f"General error: { str(e) }")
            return flask.jsonify({'message': f'保存失败: { str(e) }'}), 500

    # 接入AI分析图片
    @classmethod
    def analyzeImage(cls, filePath, fileName, userId = None):
        logging.info(f"Starting analyze_image function for { fileName } at { filePath }, user_id: { userId }")

        try:
            if (not os.path.exists(filePath)):
                logging.error(f"File not found for analysis: { filePath }")
                return flask.jsonify({
                    'message': '找不到要分析的图片文件'
                }), 404
                
            # 验证文件大小
            fileSize = os.path.getsize(filePath)

            logging.info(f"Analyzing image { fileName }, size: { fileSize } bytes")

            if (fileSize == 0):
                return flask.jsonify({
                    'message': '图片文件为空'
                }), 400

            if (fileSize > 10 * 1024 * 1024):  # 10MB限制
                return flask.jsonify({
                    'message': '图片文件太大, 请压缩后重试'
                }), 400

            # 初始化AI客户端
            try:
                # 创建自定义httpx客户端避免代理问题
                httpClient = httpx.Client()
                client = OpenAI(
                    base_url = "https://ark.cn-beijing.volces.com/api/v3",
                    api_key = "d618ffd5-dd7c-4548-8cde-a82ba550f808",
                    http_client = httpClient
                )

                logging.info("AI client initialized successfully")
            except Exception as clientError:
                logging.error(f"Failed to initialize AI client: { str(clientError) }")

                return flask.jsonify({
                    'message': f'AI客户端初始化失败: { str(clientError) }'
                }), 500

            dataUrl = cls.imageToDataUrl(filePath)

            if (not dataUrl):
                logging.error(f"Failed to convert image to data URL: { filePath }")
                return flask.jsonify({
                    'message': '图片转换失败'
                }), 500

            logging.info(f"Starting AI analysis for image: { fileName }")
            
            try:
                response = client.chat.completions.create(
                    model = "doubao-1-5-vision-pro-32k-250115",
                    messages = [{
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": { "url": dataUrl }
                            },
                            {
                                "type": "text", 
                                "text": '''
                                        你是一个专业的心理分析师, 请根据绘画静态数据：
                                        房、树、人的高清图像（需包含笔触细节）或以下结构化描述：
                                        尺寸/布局：各元素在纸上的位置、比例（如房屋占纸面50%、人物位于右下角）。
                                        线条特征：轻/重笔压、断续线条、反复涂抹区域。
                                        细节程度：门窗结构、树叶纹理、人物五官/手指等是否完整。
                                        特殊符号：天气（雨, 太阳）、附加物（围墙, 动物）
                                        进行专业分析用户的房树人绘画, 并参考以下可以涉及的分析方面：
                                        
                                        ### 绘画描述
                                        请详细描述画面中的内容, 包括房屋、树木、人物的位置、大小和特征。
                                        
                                        ### 分析概述  
                                        基于绘画内容进行整体心理状态评估。
                                        
                                        ### 具体分析
                                        从以下几个维度进行分析：
                                        1. 情绪状态：通过线条力度、色彩选择等判断
                                        2. 人际关系：通过元素间距离、比例关系等分析
                                        3. 自我认知：通过人物描绘的详细程度等评估
                                        
                                        ### 用户心理画像
                                        综合分析结果, 给出用户当前的心理状态评估和建议。
                                        
                                        若图片不是房树人相关绘画, 请温和地引导用户重新绘画房树人作品。
                                        '''
                            }
                        ]
                    }],
                    max_tokens=4000,
                    temperature=0.7
                )
                
                # 检查响应
                if (not response or not response.choices):
                    logging.error("AI service returned empty response")

                    return flask.jsonify({
                        'message': 'AI分析服务返回空响应, 请稍后重试'
                    }), 500

                # 获取分析结果
                analysisResult = response.choices[0].message.content

                if (not analysisResult or len(analysisResult.strip()) == 0):
                    logging.error("AI analysis returned empty content")

                    return flask.jsonify({
                        'message': 'AI分析返回空内容, 请稍后重试'
                    }), 500

                # 更新全局变量
                global text_result
                text_result = analysisResult

                # 保存分析结果到数据库
                if (userId):
                    try:
                        analysisId = MongoDBConfig.drawingAnalysisManager.saveAnalysis(
                            userId=userId,
                            imagePath=filePath,
                            analysisResult=analysisResult,
                            imageSize=f"{ len(open(filePath, 'rb').read()) } bytes",
                            analysisType="house_tree_person",
                            ai_model="doubao-1-5-vision-pro-32k",
                        )
                        logging.info(f"Analysis result saved to database with ID: { analysisId }")

                    except Exception as dbError:
                        logging.error(f"Failed to save analysis to database: { str(dbError) }")
                        # 继续执行, 不因为数据库保存失败而影响返回结果

                logging.info(f"Analysis completed successfully for image: { fileName }, result length: { len(analysisResult) }")

                # 构建返回数据
                returnData = {
                    'message': '分析完成',
                    'analysis': analysisResult,
                    'file_name': fileName
                }
                
                logging.info(f"Returning analysis result: { returnData }")

                return flask.jsonify(returnData), 200

            except Exception as apiError:
                logging.error(f"AI API error for { fileName }: { str(apiError) }")
                return flask.jsonify({
                    'message': 'AI分析服务暂时不可用, 请稍后重试',
                    'file_name': fileName
                }), 503
            
        except Exception as e:
            logging.error(f"General analysis error for { fileName }: { str(e) }")
            return flask.jsonify({
                'message': f'分析过程中出现错误, 请稍后重试',
                'file_name': fileName
            }), 500