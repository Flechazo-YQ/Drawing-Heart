from torch import Tensor
from torch.nn import Dropout, Linear
from transformers import BertModel, BertPreTrainedModel, BertConfig
from typing import Optional

class SimpleBertClassifier(BertPreTrainedModel):

    def __init__(self, config: BertConfig):
        super().__init__(config)

        self.bert: BertModel = BertModel(config)
        self.dropout: Dropout = Dropout(config.hidden_dropout_prob)
        self.classifier: Linear = Linear(config.hidden_size, config.num_labels)
        self.init_weights()

    def forward(self, input_ids: Tensor, attention_mask: Optional[Tensor] = None, token_type_ids: Optional[Tensor] = None):
        outputs = self.bert(
            input_ids=input_ids, 
            attention_mask=attention_mask, 
            token_type_ids=token_type_ids
        )
        pooled_output: Tensor = self.dropout(outputs[1])
        logits: Tensor = self.classifier(pooled_output)

        return logits