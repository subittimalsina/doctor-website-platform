from datetime import datetime

from pydantic import BaseModel


class SupportTicketCreate(BaseModel):
    subject: str
    category: str
    priority: str
    message: str


class SupportMessageRead(BaseModel):
    id: int
    sender_role: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
