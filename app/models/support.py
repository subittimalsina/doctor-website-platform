from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general")
    priority: Mapped[str] = mapped_column(String(30), default="normal")
    status: Mapped[str] = mapped_column(String(30), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tickets")
    messages = relationship("SupportMessage", back_populates="ticket", cascade="all,delete")


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    sender_role: Mapped[str] = mapped_column(String(30), default="patient")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ticket = relationship("SupportTicket", back_populates="messages")
