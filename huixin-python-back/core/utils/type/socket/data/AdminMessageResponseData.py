from pydantic import BaseModel

class AdminMessageResponseData(BaseModel):
    status: str
    message: str