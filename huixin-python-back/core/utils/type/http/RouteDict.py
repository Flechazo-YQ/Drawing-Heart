from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class RouteDict:
    route: str
    method: List[str]