from pydantic import BaseModel

class AdminReplyData(BaseModel):
    chatId: str
    content: str
    timestamp: str