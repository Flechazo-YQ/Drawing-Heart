from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, Final, Type, Callable

class FormatHelper:
    TYPE_HANDLE_CONFIG: Final[Dict[Type, Callable[[Any], Any]]] = {
        ObjectId: str,
        datetime: lambda dt: dt.isoformat() + 'Z'
    }

    @classmethod
    def json(cls, data: Any) -> Any:
        if (data is None): return None

        handler = cls.TYPE_HANDLE_CONFIG.get(type(data))

        if (handler): return handler(data)
        if (isinstance(data, dict)): return { key: cls.json(value) for key, value in data.items() }
        if (isinstance(data, list)): return [cls.json(item) for item in data]

        return data

    @classmethod
    def __formatValue(cls, value: Any) -> Any:
        if (isinstance(value, Dict)): return cls.json(value)
        if (isinstance(value, list)): return [cls.__formatValue(v) for v in value]

        handler = cls.TYPE_HANDLE_CONFIG.get(type(value))

        if (handler): return handler(value)

        return value
