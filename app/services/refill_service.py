from datetime import datetime

from sqlalchemy.orm import Session

from app.models import RefillRequest


class RefillService:
    @staticmethod
    def create_request(
        db: Session,
        patient_id: int,
        medication_name: str,
        dosage: str,
        current_supply_days: int,
        pharmacy_name: str,
        pharmacy_phone: str,
        notes: str,
    ) -> RefillRequest:
        req = RefillRequest(
            patient_id=patient_id,
            medication_name=medication_name.strip(),
            dosage=dosage.strip(),
            current_supply_days=current_supply_days,
            pharmacy_name=pharmacy_name.strip(),
            pharmacy_phone=pharmacy_phone.strip(),
            notes=notes.strip(),
            status="submitted",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def set_status(
        db: Session,
        refill: RefillRequest,
        status: str,
        reviewed_by: str,
        decision_note: str,
    ) -> RefillRequest:
        refill.status = status
        refill.reviewed_by = reviewed_by.strip()
        refill.decision_note = decision_note.strip()
        refill.updated_at = datetime.utcnow()
        db.add(refill)
        db.commit()
        db.refresh(refill)
        return refill

    @staticmethod
    def list_for_patient(db: Session, patient_id: int) -> list[RefillRequest]:
        return (
            db.query(RefillRequest)
            .filter(RefillRequest.patient_id == patient_id)
            .order_by(RefillRequest.updated_at.desc())
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> list[RefillRequest]:
        return db.query(RefillRequest).order_by(RefillRequest.updated_at.desc()).all()
