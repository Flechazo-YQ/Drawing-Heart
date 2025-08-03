import torch.nn as nn

from transformers import BertModel, BertPreTrainedModel

class SimpleBertClassifier(BertPreTrainedModel):
    
    def __init__(self, config):
        super().__init__(config)

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.init_weights()

    def forward(self, inputIds, attentionMask=None, tokenTypeIds=None):
        outputs = self.bert(input_ids=inputIds, attention_mask=attentionMask, token_type_ids=tokenTypeIds)
        pooled_output = self.dropout(outputs[1])
        logits = self.classifier(pooled_output)

        return logits