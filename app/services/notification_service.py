from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Notification


class NotificationService:
    @staticmethod
    def send(db: Session, user_id: int, title: str, message: str, kind: str = "system") -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title.strip(),
            message=message.strip(),
            kind=kind,
            is_read=False,
            created_at=datetime.utcnow(),
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def list_for_user(db: Session, user_id: int) -> list[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_read(db: Session, notification_id: int, user_id: int) -> bool:
        notif = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if not notif:
            return False
        notif.is_read = True
        db.add(notif)
        db.commit()
        return True
