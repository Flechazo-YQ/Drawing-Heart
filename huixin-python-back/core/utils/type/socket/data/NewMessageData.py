from typing import TypedDict

class NewMessageData(TypedDict):
    userId: str
    chatId: str
    role: str
    content: str
    timestamp: str