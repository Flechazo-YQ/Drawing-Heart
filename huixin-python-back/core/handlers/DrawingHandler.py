import os, logging, flask

from core.configs.MongoDBConfig import MongoDBConfig
from core.utils.ImageHelper import ImageHelper

from openai import OpenAI
from httpx import Client

class DrawingHandler:
        
    # 接入AI分析图片
    @classmethod
    def analyzeImage(cls, filePath: str, fileName: str, userId: str | None = None):
        logging.info(f'分析图片: { fileName } : { filePath }, 用户ID: { userId }')

        try:
            if (not os.path.exists(filePath)):
                logging.error(f'❌ 文件未找到: { filePath }')
                return flask.jsonify({
                    'message': '找不到要分析的图片文件'
                }), 404
                
            # 验证文件大小
            fileSize = os.path.getsize(filePath)

            logging.info(f'正在分析图片 { fileName }, 大小: { fileSize } bytes')

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
                httpClient = Client()
                client = OpenAI(
                    base_url = 'https://ark.cn-beijing.volces.com/api/v3',
                    api_key = 'd618ffd5-dd7c-4548-8cde-a82ba550f808',
                    http_client = httpClient
                )

                logging.info('AI客户端初始化成功')
            except Exception as clientError:
                logging.error(f'❌ AI客户端初始化失败: { str(clientError) }')

                return flask.jsonify({
                    'message': f'AI客户端初始化失败: { str(clientError) }'
                }), 500

            dataUrl = ImageHelper.imageToDataUrl(filePath)

            if (not dataUrl):
                logging.error(f'❌ 图片转换失败: { filePath }')
                return flask.jsonify({
                    'message': '图片转换失败'
                }), 500

            logging.info(f'开始图片AI分析: { fileName }')

            try:
                response = client.chat.completions.create(
                    model = 'doubao-1-5-vision-pro-32k-250115',
                    messages = [ # type: ignore
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': dataUrl
                                    }
                                },
                                {
                                    'type': 'text',
                                    'text': '''
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
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
                
                # 检查响应
                if (not response or not response.choices):
                    logging.error(f'❌ AI服务返回空响应')

                    return flask.jsonify({
                        'message': 'AI分析服务返回空响应, 请稍后重试'
                    }), 500

                # 获取分析结果
                analysisResult = response.choices[0].message.content

                if (not analysisResult or len(analysisResult.strip()) == 0):
                    logging.error(f'❌ AI分析返回空内容')

                    return flask.jsonify({
                        'message': 'AI分析返回空内容, 请稍后重试'
                    }), 500

                # 保存分析结果到数据库
                if (userId):
                    try:
                        analysisId = MongoDBConfig.drawingManager.saveAnalysis(
                            userId=userId,
                            imagePath=filePath,
                            analysisResult=analysisResult,
                            imageSize=f'{ len(open(filePath, "rb").read()) } bytes',
                            analysisType='house_tree_person',
                            aiModel='doubao-1-5-vision-pro-32k',
                        )
                        logging.info(f'分析结果已保存到数据库, ID: { analysisId }')

                    except Exception as dbError:
                        logging.error(f'❌ 保存分析到数据库失败: { str(dbError) }')
                        # 继续执行, 不因为数据库保存失败而影响返回结果

                logging.info(f'分析完成: { fileName }, 结果长度: { len(analysisResult) }')

                # 构建返回数据
                returnData = {
                    'message': '分析完成',
                    'analysis': analysisResult,
                    'fileName': fileName
                }

                logging.info(f'返回分析结果: { returnData }')

                return flask.jsonify(returnData), 200

            except Exception as apiError:
                logging.error(f'❌ AI API错误: { fileName }: { str(apiError) }')
                return flask.jsonify({
                    'message': 'AI分析服务暂时不可用, 请稍后重试',
                    'fileName': fileName
                }), 503
            
        except Exception as e:
            logging.error(f'❌ 一般分析错误: { fileName }: { str(e) }')
            return flask.jsonify({
                'message': f'分析过程中出现错误, 请稍后重试',
                'fileName': fileName
            }), 500