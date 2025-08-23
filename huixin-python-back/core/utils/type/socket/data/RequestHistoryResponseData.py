from typing import TypedDict, List, Any

class RequestHistoryResponseData(TypedDict):
    chatId: str
    messages: List[Any]