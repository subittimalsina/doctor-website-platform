from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    actor_email: Mapped[str] = mapped_column(String(255), default="system")
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), default="generic")
    target_id: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
