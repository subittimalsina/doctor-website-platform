from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Appointment


class AppointmentService:
    @staticmethod
    def create_appointment(db: Session, patient_id: int, reason: str, notes: str, appointment_time: datetime) -> Appointment:
        appointment = Appointment(
            patient_id=patient_id,
            reason=reason.strip(),
            notes=notes.strip(),
            appointment_time=appointment_time,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def set_status(db: Session, appointment_id: int, status: str) -> bool:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return False
        appt.status = status
        db.add(appt)
        db.commit()
        return True
