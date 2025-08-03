import datetime, logging

from core.configs.MongoDBConfig import MongoDBConfig

from typing import Dict, List, Optional
from bson import ObjectId

class DrawingAnalysisManager:

    def __init__(self, db: MongoDBConfig.MongoDB):
        self.db = db
    
    # 保存绘画分析结果, 返回分析记录ID
    def saveAnalysis(self, userId: str, imagePath: str, analysisResult: str, **kwargs) -> str:
        analysisData = {
            "user_id": ObjectId(userId),
            "image_path": imagePath,
            "analysis_result": analysisResult,
            "analysis_date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),  # 只保存日期部分
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "metadata": {
                "image_size": kwargs.get("image_size", ""),
                "analysis_type": kwargs.get("analysis_type", "house_tree_person"),
                "ai_model": kwargs.get("ai_model", "doubao-1-5-vision-pro"),
                "confidence_score": kwargs.get("confidence_score", 0.0),
                "analysis_duration": kwargs.get("analysis_duration", 0),  # 分析耗时（秒）
            },
            "tags": kwargs.get("tags", []),  # 分析标签，如["焦虑", "抑郁", "积极"]
            "emotional_indicators": {
                "anxiety_level": kwargs.get("anxiety_level", 0),
                "depression_level": kwargs.get("depression_level", 0),
                "stress_level": kwargs.get("stress_level", 0),
                "confidence_level": kwargs.get("confidence_level", 0),
                "creativity_level": kwargs.get("creativity_level", 0),
            },
            "is_active": True
        }

        result = self.db.drawingAnalyses.insert_one(analysisData)

        return str(result.inserted_id)

    # 获取用户当日的绘画分析结果
    def getTodayAnalysis(self, userId: str) -> Optional[Dict]:
        try:
            today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            analysis = self.db.drawingAnalyses.find_one(
                {
                    "user_id": ObjectId(userId),
                    "analysis_date": today,
                    "is_active": True
                }, 
                sort=[("created_at", -1)]
            )  # 获取当日最新的分析结果
            
            if (analysis):
                analysis["_id"] = str(analysis["_id"])
                analysis["user_id"] = str(analysis["user_id"])
            
            return analysis
        except Exception as e:
            logging.error(f"获取当日分析结果失败: { str(e) }")

            return None
    
    # 获取用户最新的绘画分析结果(不限日期)
    def getLatestAnalysis(self, userId: str) -> Optional[Dict]:
        try:
            analysis = self.db.drawingAnalyses.find_one(
                {
                    "user_id": ObjectId(userId),
                    "is_active": True
                }, 
                sort=[("created_at", -1)]
            )  # 按创建时间降序，获取最新的分析结果
            
            if (analysis):
                analysis["_id"] = str(analysis["_id"])
                analysis["user_id"] = str(analysis["user_id"])
            
            return analysis
        except Exception as e:
            logging.error(f"获取最新分析结果失败: { str(e) }")
            return None

    # 获取用户在指定小时内的最新绘画分析结果
    # 如果是0小时，则获取当日的分析结果
    def getRecentAnalysis(self, userId: str, hours: int = 4) -> Optional[Dict]:
        try:
            currentTime = datetime.datetime.utcnow()
            
            if (hours == 0):
                # 获取当日分析结果
                startOfDay = currentTime.replace(hour=0, minute=0, second=0, microsecond=0)
                endOfDay = startOfDay + datetime.timedelta(days=1)
                timeFilter = {
                    "created_at": {
                        "$gte": startOfDay,
                        "$lt": endOfDay
                    }
                }
            else:
                # 获取指定小时内的分析结果
                timeThreshold = currentTime - datetime.timedelta(hours=hours)
                timeFilter = {
                    "created_at": {"$gte": timeThreshold}
                }

            analysis = self.db.drawingAnalyses.find_one(
                {
                    "user_id": ObjectId(userId),
                    "is_active": True,
                    **timeFilter
                }, 
                sort=[("created_at", -1)]
            )  # 按创建时间降序，获取最新的分析结果
            
            if (analysis):
                analysis["_id"] = str(analysis["_id"])
                analysis["user_id"] = str(analysis["user_id"])
            
            return analysis
        except Exception as e:
            logging.error(f"获取近期分析结果失败: { str(e) }")
            return None

    # 获取用户的历史分析结果
    def getUserAnalyses(self, userId: str, limit: int = 10, page: int = 1) -> List[Dict]:
        try:
            skip = (page - 1) * limit
            analyses = list(self.db.drawingAnalyses.find(
                {
                    "user_id": ObjectId(userId),
                    "is_active": True
                })
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            
            # 转换ObjectId为字符串
            for analysis in analyses:
                analysis["_id"] = str(analysis["_id"])
                analysis["user_id"] = str(analysis["user_id"])
            
            return analyses
        except Exception as e:
            logging.error(f"获取用户分析历史失败: { str(e) }")
            return []

    # 获取用户指定日期范围内的分析结果
    def getAnalysisByDateRange(self, userId: str, startDate: str, endDate: str) -> List[Dict]:
        try:
            analyses = list(self.db.drawingAnalyses.find({
                "user_id": ObjectId(userId),
                "analysis_date": {
                    "$gte": startDate, 
                    "$lte": endDate
                },
                "is_active": True
            }).sort("analysis_date", -1))
            
            # 转换ObjectId为字符串
            for analysis in analyses:
                analysis["_id"] = str(analysis["_id"])
                analysis["user_id"] = str(analysis["user_id"])
            
            return analyses
        except Exception as e:
            logging.error(f"获取日期范围分析结果失败: { str(e) }")
            return []
    
    # 更新分析结果
    def updateAnalysis(self, analysisId: str, updateData: Dict) -> bool:
        try:
            updateData["updated_at"] = datetime.datetime.utcnow()
            result = self.db.drawingAnalyses.update_one(
                {"_id": ObjectId(analysisId)},
                {"$set": updateData}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"更新分析结果失败: { str(e) }")
            return False
    
    # 软删除分析结果
    def deleteAnalysis(self, analysisId: str) -> bool:
        try:
            result = self.db.drawingAnalyses.update_one(
                {"_id": ObjectId(analysisId)},
                {
                    "$set": {
                        "is_active": False, 
                        "updated_at": datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"删除分析结果失败: { str(e) }")
            return False