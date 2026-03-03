from datetime import datetime

from sqlalchemy.orm import Session

from app.models import MedicalRecord, Prescription


class RecordService:
    @staticmethod
    def create_record(
        db: Session,
        patient_id: int,
        record_title: str,
        diagnosis_summary: str,
        observations: str,
        recommendations: str,
        created_by: str,
    ) -> MedicalRecord:
        record = MedicalRecord(
            patient_id=patient_id,
            record_title=record_title.strip(),
            diagnosis_summary=diagnosis_summary.strip(),
            observations=observations.strip(),
            recommendations=recommendations.strip(),
            status="active",
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_record(
        db: Session,
        record: MedicalRecord,
        record_title: str,
        diagnosis_summary: str,
        observations: str,
        recommendations: str,
        status: str,
    ) -> MedicalRecord:
        record.record_title = record_title.strip()
        record.diagnosis_summary = diagnosis_summary.strip()
        record.observations = observations.strip()
        record.recommendations = recommendations.strip()
        record.status = status
        record.updated_at = datetime.utcnow()
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete_record(db: Session, record_id: int) -> bool:
        record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        if not record:
            return False
        db.delete(record)
        db.commit()
        return True

    @staticmethod
    def add_prescription(
        db: Session,
        record_id: int,
        medicine_name: str,
        dosage: str,
        schedule: str,
        duration: str,
        notes: str,
    ) -> Prescription:
        prescription = Prescription(
            record_id=record_id,
            medicine_name=medicine_name.strip(),
            dosage=dosage.strip(),
            schedule=schedule.strip(),
            duration=duration.strip(),
            notes=notes.strip(),
            created_at=datetime.utcnow(),
        )
        db.add(prescription)
        db.commit()
        db.refresh(prescription)
        return prescription

    @staticmethod
    def delete_prescription(db: Session, prescription_id: int) -> bool:
        item = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
