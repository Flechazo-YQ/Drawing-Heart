from pydantic import BaseModel

class NewMessageData(BaseModel):
    userId: str
    chatId: str
    role: str
    content: str
    timestamp: str