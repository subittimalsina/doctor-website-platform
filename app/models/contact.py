from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ContactLead(Base):
    __tablename__ = "contact_leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), default="")
    subject: Mapped[str] = mapped_column(String(255), default="General Inquiry")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
