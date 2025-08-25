from pydantic import BaseModel
from typing import Dict, Any, List

class DangerousChatsListData(BaseModel):
    chats: List[Dict[str, Any]]