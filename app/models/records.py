from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    record_title: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosis_summary: Mapped[str] = mapped_column(String(500), default="")
    observations: Mapped[str] = mapped_column(Text, default="")
    recommendations: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    created_by: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    prescriptions = relationship("Prescription", back_populates="record", cascade="all,delete")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(Integer, ForeignKey("medical_records.id"), index=True)
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(255), default="")
    schedule: Mapped[str] = mapped_column(String(255), default="")
    duration: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    record = relationship("MedicalRecord", back_populates="prescriptions")
