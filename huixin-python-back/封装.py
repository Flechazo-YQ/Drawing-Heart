import torch
import re
import pandas as pd
from transformers import BertTokenizer, BertModel, BertPreTrainedModel, BertConfig
import torch.nn as nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_slang_map(slang_file="slang_map.csv"):
    slang_dict = {}
    slang_df = pd.read_csv(slang_file, encoding='gb18030')
    for _, row in slang_df.iterrows():
        slang_dict[row['slang']] = row['normalized']
    return slang_dict


class SimpleBertClassifier(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.init_weights()

    def forward(self, input_ids, attention_mask=None, token_type_ids=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        pooled_output = self.dropout(outputs[1])
        logits = self.classifier(pooled_output)
        return logits


# 封装的推理类
class EmotionClassifier:
    def __init__(self, model_path="./emotion_model", slang_file="slang_map.csv"):
        self.label_map = {0: "危险", 1: "负面", 2: "其他"}
        self.slang_dict = load_slang_map(slang_file)

        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        config = BertConfig.from_pretrained(model_path)
        self.model = SimpleBertClassifier.from_pretrained(model_path, config=config).to(device)
        self.model.eval()

    def normalize(self, text):
        text = str(text)
        text = re.sub(r'\d+', '<NUM>', text)
        for slang, norm in self.slang_dict.items():
            text = text.replace(slang, norm)
        return text

    def predict(self, text):
        text = self.normalize(text)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            pred_label = self.label_map[probs.argmax()]
            return pred_label, probs
