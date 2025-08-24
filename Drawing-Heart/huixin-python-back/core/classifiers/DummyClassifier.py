from typing import Tuple, List, Dict, Final

class DummyClassifier:
    DANGER_KEYWORDS: Final[List[str]] = [
        '自杀', '自残', '死', '想死', '活不下去', 
        '结束生命', '轻生', '跳楼', '割腕', '上吊'
    ]
    NEGATIVE_KEYWORDS: Final[List[str]] = [
        '难过', '痛苦', '绝望', '孤独', '抑郁',
        '焦虑', '失望', '伤心', '无助', '沮丧'
    ]
    LABEL_MAP: Final[Dict[int, str]] = {
        0: "危险",
        1: "负面",
        2: "其他"
    }
    
    def predict(self, text: str) -> Tuple[str, List[float]]:
        text = text.lower()
        
        # 检查是否包含危险关键词
        for keyword in self.DANGER_KEYWORDS:
            if (keyword in text):
                return ("危险", [0.8, 0.1, 0.1])  # 高危险概率
                
        # 检查是否包含负面关键词
        for keyword in self.NEGATIVE_KEYWORDS:
            if (keyword in text):
                return ("负面", [0.1, 0.7, 0.2])  # 高负面概率
                
        # 默认为其他
        return ("其他", [0.05, 0.15, 0.8])  # 低危险概率