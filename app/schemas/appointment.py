from datetime import datetime

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    reason: str
    notes: str = ""
    appointment_time: datetime


class AppointmentRead(BaseModel):
    id: int
    reason: str
    notes: str
    appointment_time: datetime
    status: str

    class Config:
        from_attributes = True
