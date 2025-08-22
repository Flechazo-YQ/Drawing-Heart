from typing import List, TypedDict, Callable, Dict, Any

class TypedDictionaryHelper:

    # 绘画分析函数Config类型信息
    class AnalysisTimeItem(TypedDict):
        query: Callable[[str], object]  # 你可以根据实际返回类型替换 object
        desc: str

    class AnalysisTimeConfig(TypedDict):
        today: 'TypedDictionaryHelper.AnalysisTimeItem'
        _4hours: 'TypedDictionaryHelper.AnalysisTimeItem'
        recent: 'TypedDictionaryHelper.AnalysisTimeItem'
        none: 'TypedDictionaryHelper.AnalysisTimeItem'

    # 路由信息
    class Route(TypedDict):
        route: str
        method: List[str]

    # Socket事件信息
    class Socket(TypedDict):
        event: str
        data: Any

    class RequestHistoryResponseData(TypedDict):
        chatId: str
        messages: List[Any]

    class NewMessageData(TypedDict):
        userId: str
        chatId: str
        role: str
        content: str
        timestamp: str

    class DangerousChatsListData(TypedDict):
        chats: Dict[str, Any]

    class AdminMessageResponseData(TypedDict):
        status: str
        message: str

    class AdminReplyData(TypedDict):
        chatId: str
        content: str
        timestamp: str