import re, torch, pandas, logging

from core.classifiers.SimpleBertClassifier import SimpleBertClassifier

from transformers import BertTokenizer, BertConfig
from torch import device, cuda
from numpy import ndarray
from typing import Dict, Tuple, Final

class EmotionClassifier:
    DEVICE: Final[device] = device("cuda" if (cuda.is_available()) else "cpu")
    LABEL_MAP: Final[Dict[int, str]] = { 
        0: "危险", 
        1: "负面", 
        2: "其他" 
    }

    def __init__(self, modelPath: str = "./emotion_model", slangFile: str = "slang_map.csv"):
        self.slangDict: Dict[str, str] = self.__loadSlangMap(slangFile)
        self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(modelPath)
        config: BertConfig = BertConfig.from_pretrained(modelPath)
        self.model = SimpleBertClassifier.from_pretrained(modelPath, config=config).to(self.DEVICE) # type: ignore

        # # 打印模型参数检查
        # param_stats = {
        #     "总参数数量": sum(p.numel() for p in self.model.parameters()),
        #     "参数总和": sum(p.sum().item() for p in self.model.parameters()),
        #     "分类器权重总和": sum(p.sum().item() for p in self.model.classifier.parameters())
        # }
        # logging.info(f"模型参数统计: {param_stats}")

        self.model.eval()

    # 预测情感
    def predict(self, text: str) -> Tuple[str, ndarray]:

        # ==========================================================
        # 测试代码(未来删除)
        if (hasattr(self, '_is_classifier_reset') == False):
            import torch.nn as nn
            # 重新初始化分类器层
            nn.init.xavier_normal_(self.model.classifier.weight)
            nn.init.zeros_(self.model.classifier.bias)
            self._is_classifier_reset = True
            logging.info("✅ 已重置分类器层权重")
        # ===========================================================
            
        text = self.__normalize(text)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = { key: value.to(self.DEVICE) for (key, value) in inputs.items() }

        with torch.no_grad():
            logits = self.model(**inputs)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            predLabel = self.LABEL_MAP[probs.argmax()]

            return (predLabel, probs)

    # 加载俚语映射
    @staticmethod
    def __loadSlangMap(slangFile: str = "slang_map.csv") -> Dict[str, str]:
        slangDict: Dict[str, str] = {}

        try:
            # 尝试不同的编码方式
            for encoding in ['utf-8', 'gb18030', 'gbk', 'utf-8-sig']:
                try:
                    slangDf = pandas.read_csv(slangFile, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 如果所有编码都失败，创建默认数据
                slangDf = pandas.DataFrame({
                    'slang': ['nb', '666', 'yyds', 'tql'],
                    'normalized': ['牛逼', '厉害', '永远的神', '太强了']
                })
        except Exception as e:
            logging.error(f"❌ 加载slang_map文件出错: { str(e) }")

            # 创建默认数据
            slangDf = pandas.DataFrame({
                'slang': ['nb', '666', 'yyds', 'tql'],
                'normalized': ['牛逼', '厉害', '永远的神', '太强了']
            })

        for (_, row) in slangDf.iterrows():
            slangDict[row['slang']] = row['normalized']

        return slangDict

    # 文本规范化
    def __normalize(self, text: str) -> str:
        text = re.sub(r'\d+', '<NUM>', text)

        for (slang, norm) in self.slangDict.items():
            text = text.replace(slang, norm)
            
        return text