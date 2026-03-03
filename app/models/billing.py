from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(500), default="Clinic service")
    amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="unpaid")
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    events = relationship("PaymentEvent", back_populates="invoice", cascade="all,delete")


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), default="created")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="events")
