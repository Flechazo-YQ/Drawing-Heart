import datetime, logging

from core.utils.FormatHelper import FormatHelper

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from bson import ObjectId

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class DrawingManager:
    class Updater:
        ALLOWED_INDICATORS = ["anxietyLevel", "depressionLevel", "stressLevel", "confidenceLevel", "creativityLevel"]

        def __init__(self, db: "MongoDBConfig.MongoDB"):
            self.db = db

        def text(self, analysisId: str, newText: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(analysisId)
                }
                updateQuery = {
                    "$set": {
                        "analysis.resultText": newText,
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.drawings.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 更新绘画分析结果失败: { str(e) }")
                return False
            
        def addTag(self, analysisId: str, tag: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(analysisId)
                }
                updateQuery = {
                    "$addToSet": {
                        "analysis.tags": tag
                    },
                    "$set": {
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.drawings.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 添加标签失败: { str(e) }")
                return False

        def removeTag(self, analysisId: str, tag: str) -> bool:
            try:
                idFilter = {
                    "_id": ObjectId(analysisId)
                }
                updateQuery = {
                    "$pull": {
                        "analysis.tags": tag
                    },
                    "$set": {
                        "timeNode.updatedAt": datetime.now(timezone.utc)
                    }
                }
                result = self.db.drawings.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 删除标签失败: { str(e) }")
                return False
            
        def indicators(self, analysisId: str, **newIndicators) -> bool:
            try:
                updateFields = {}

                for (key, value) in newIndicators.items():
                    if (key in self.ALLOWED_INDICATORS):
                        updateFields[f"analysis.indicators.{ key }"] = value

                if (not updateFields):
                    logging.warning("⚠️ 没有有效的情感指标更新")
                    return False
                
                updateFields["timeNode.updatedAt"] = datetime.now(timezone.utc)
                idFilter = {
                    "_id": ObjectId(analysisId)
                }
                updateQuery = {
                    "$set": updateFields
                }
                result = self.db.drawings.update_one(idFilter, updateQuery)

                return result.modified_count > 0
            except Exception as e:
                logging.error(f"❌ 更新情感指标失败: { str(e) }")
                return False

    def __init__(self, db: "MongoDBConfig.MongoDB"):
        self.db = db
        self.updater = self.Updater(db)

    # 保存绘画分析结果, 返回分析记录ID
    def saveAnalysis(self, userId: str, imagePath: str, analysisResult: str, **kwargs) -> str:
        analysisData = {

            # 核心关系与索引字段
            "userId": userId,

            # 图片路径
            "imagePath": imagePath,

            # 状态与时间戳
            "stats": {
                "isActive": True       # 用于软删除
            },
            "timeNode": {
                "createdAt": datetime.now(timezone.utc), # 关键：用于排序和时间范围查询
                "updatedAt": datetime.now(timezone.utc)
            },

            # 分析结果
            "analysis": {
                "resultText": analysisResult, # 详细的文本分析结果
                "tags": kwargs.get("tags", []), # 关键词标签，如["焦虑", "积极"]
                "indicators": { # 结构化的情感指标
                    "anxietyLevel": kwargs.get("anxietyLevel", 0),
                    "depressionLevel": kwargs.get("depressionLevel", 0),
                    "stressLevel": kwargs.get("stressLevel", 0),
                    "confidenceLevel": kwargs.get("confidenceLevel", 0),
                    "creativityLevel": kwargs.get("creativityLevel", 0),
                }
            },

            # 元数据
            "metadata": {
                "imageSize": kwargs.get("imageSize", ""),
                "analysisType": kwargs.get("analysisType", "houseTreePerson"),
                "aiModel": kwargs.get("aiModel", "doubao-1-5-vision-pro"),
                "confidenceScore": kwargs.get("confidenceScore", 0.0),
                "analysisDuration": kwargs.get("analysisDuration", 0) # 分析耗时（秒）
            }
        }

        self.db.drawings.insert_one(analysisData)

        return FormatHelper.jsonOrList(analysisData)

    # 获取用户当日的绘画分析结果
    def getTodayAnalysis(self, userId: str) -> Optional[Dict]:
        try:
            now = datetime.now(timezone.utc)
            startOfDay = now.replace(hour=0, minute=0, second=0, microsecond=0)
            idFilter = {
                "userId": ObjectId(userId),
                "stats.isActive": True,
                "timeNode.createdAt": {
                    "$gte": startOfDay
                }
            }
            sort = [("timeNode.createdAt", -1)]
            analysis = self.db.drawings.find_one(idFilter, sort=sort)  # 获取当日最新的分析结果

            return FormatHelper.jsonOrList(analysis) if (analysis) else None
        except Exception as e:
            logging.error(f"❌ 获取当日分析结果失败: { str(e) }")
            return None
    
    # 获取用户最新的绘画分析结果(不限日期)
    def getLatestAnalysis(self, userId: str) -> Optional[Dict]:
        try:
            idFilter = {
                "userId": ObjectId(userId),
                "stats.isActive": True
            }
            sort = [("timeNode.createdAt", -1)]
            analysis = self.db.drawings.find_one(idFilter, sort=sort)  # 按创建时间降序，获取最新的分析结果

            return FormatHelper.jsonOrList(analysis) if (analysis) else None
        except Exception as e:
            logging.error(f"❌ 获取最新分析结果失败: { str(e) }")
            return None

    # 获取用户在指定小时内的最新绘画分析结果
    # 如果是0小时，则获取当日的分析结果
    def getRecentAnalysis(self, userId: str, hours: int = 4) -> Optional[Dict]:
        try:
            timeThreshold = datetime.now(timezone.utc) - timedelta(hours=hours)
            idFilter = {
                "userId": ObjectId(userId),
                "stats.isActive": True,
                "timeNode.createdAt": {
                    "$gte": timeThreshold
                }
            }
            sort = [("timeNode.createdAt", -1)]
            analysis = self.db.drawings.find_one(idFilter, sort=sort)

            return FormatHelper.jsonOrList(analysis) if (analysis) else None
        except Exception as e:
            logging.error(f"❌ 获取近期分析结果失败: { str(e) }")
            return None

    # 获取用户的历史分析结果
    def getUserAnalyses(self, userId: str, limit: int = 10, page: int = 1) -> Tuple[List[Dict], int]:
        try:
            skip = (page - 1) * limit
            idFilter = {
                "userId": ObjectId(userId),
                "stats.isActive": True
            }
            total = self.db.drawings.count_documents(idFilter)
            analyses = list(self.db.drawings.find(idFilter)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit))

            return (FormatHelper.jsonOrList(analyses), total)
        except Exception as e:
            logging.error(f"❌ 获取用户分析历史失败: { str(e) }")
            return ([], 0)

    # 获取用户指定日期范围内的分析结果
    def getAnalysisByDateRange(self, userId: str, startDate: datetime, endDate: datetime) -> Tuple[List[Dict], int]:
        try:
            endOfDayEndDate = endDate.replace(hour=23, minute=59, second=59, microsecond=999999)
            idFilter = {
                "userId": ObjectId(userId),
                "stats.isActive": True,
                "timeNode.createdAt": {
                    "$gte": startDate,
                    "$lte": endOfDayEndDate
                }
            }
            sort = [("timeNode.createdAt", -1)]
            total = self.db.drawings.count_documents(idFilter)
            analyses = list(self.db.drawings.find(idFilter).sort(sort))

            return (FormatHelper.jsonOrList(analyses), total)
        except Exception as e:
            logging.error(f"❌ 获取日期范围分析结果失败: { str(e) }")
            return ([], 0)
