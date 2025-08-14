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
        self.slangDict: Dict[str, str] = self.loadSlangMap(slangFile)

        self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(modelPath)
        config: BertConfig = BertConfig.from_pretrained(modelPath)
        self.model = SimpleBertClassifier.from_pretrained(modelPath, config=config).to(self.DEVICE) # type: ignore
        self.model.eval()

    @staticmethod
    def loadSlangMap(slangFile: str = "slang_map.csv") -> Dict[str, str]:
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

        for _, row in slangDf.iterrows():
            slangDict[row['slang']] = row['normalized']

        return slangDict

    def normalize(self, text: str) -> str:
        text = re.sub(r'\d+', '<NUM>', text)

        for slang, norm in self.slangDict.items():
            text = text.replace(slang, norm)
            
        return text

    def predict(self, text: str) -> Tuple[str, ndarray]:
        text = self.normalize(text)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = { k: v.to(self.DEVICE) for k, v in inputs.items() }

        with torch.no_grad():

            logits = self.model(**inputs)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            predLabel = self.LABEL_MAP[probs.argmax()]

            return (predLabel, probs)