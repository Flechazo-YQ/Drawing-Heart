import logging

class DummyClassifier:
    """虚拟分类器，用于在真实分类器无法加载时提供基本功能"""
    
    def __init__(self):
        self.labelMap = { 
            0: "危险", 
            1: "负面", 
            2: "其他" 
        }
        logging.warning("使用虚拟分类器，危险检测基于关键词")
    
    def predict(self, text):
        """基于关键词的简单危险检测"""
        text = str(text).lower()
        
        # 危险关键词列表
        danger_keywords = [
            '自杀', '自残', '死', '想死', '活不下去', 
            '结束生命', '轻生', '跳楼', '割腕', '上吊'
        ]
        
        # 负面关键词列表  
        negative_keywords = [
            '难过', '痛苦', '绝望', '孤独', '抑郁',
            '焦虑', '失望', '伤心', '无助', '沮丧'
        ]
        
        # 检查是否包含危险关键词
        for keyword in danger_keywords:
            if keyword in text:
                return "危险", [0.8, 0.1, 0.1]  # 高危险概率
                
        # 检查是否包含负面关键词
        for keyword in negative_keywords:
            if keyword in text:
                return "负面", [0.1, 0.7, 0.2]  # 高负面概率
                
        # 默认为其他
        return "其他", [0.05, 0.15, 0.8]  # 低危险概率