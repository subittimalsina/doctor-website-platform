from datetime import datetime

from pydantic import BaseModel


class AIMessageRead(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
