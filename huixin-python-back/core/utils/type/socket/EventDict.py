from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EventDict:
    event: str
    data: Any