from pydantic import BaseModel
from typing import List, Any

class RequestHistoryResponseData(BaseModel):
    chatId: str
    messages: List[Any]