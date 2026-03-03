from datetime import datetime

from sqlalchemy.orm import Session

from app.models import ContactLead


class ContactService:
    @staticmethod
    def create_lead(
        db: Session,
        full_name: str,
        email: str,
        phone: str,
        subject: str,
        message: str,
    ) -> ContactLead:
        lead = ContactLead(
            full_name=full_name.strip(),
            email=email.strip().lower(),
            phone=phone.strip(),
            subject=subject.strip() or "General Inquiry",
            message=message.strip(),
            status="new",
            created_at=datetime.utcnow(),
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def list_leads(db: Session) -> list[ContactLead]:
        return db.query(ContactLead).order_by(ContactLead.created_at.desc()).all()

    @staticmethod
    def set_status(db: Session, lead_id: int, status: str) -> bool:
        lead = db.query(ContactLead).filter(ContactLead.id == lead_id).first()
        if not lead:
            return False
        lead.status = status
        db.add(lead)
        db.commit()
        return True
