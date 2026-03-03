from datetime import datetime

from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditService:
    @staticmethod
    def log(
        db: Session,
        actor_email: str,
        action: str,
        target_type: str = "generic",
        target_id: str = "",
        notes: str = "",
    ) -> AuditLog:
        event = AuditLog(
            actor_email=actor_email,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            notes=notes,
            created_at=datetime.utcnow(),
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def recent(db: Session, limit: int = 50) -> list[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
