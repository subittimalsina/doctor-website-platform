from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Announcement


class AnnouncementService:
    @staticmethod
    def list_published(db: Session) -> list[Announcement]:
        now = datetime.utcnow()
        return (
            db.query(Announcement)
            .filter(Announcement.status == "published")
            .filter(Announcement.publish_start <= now)
            .filter(Announcement.publish_end >= now)
            .order_by(Announcement.importance.desc(), Announcement.publish_start.desc())
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> list[Announcement]:
        return db.query(Announcement).order_by(Announcement.created_at.desc()).all()

    @staticmethod
    def create(
        db: Session,
        title: str,
        content: str,
        importance: str,
        status: str,
        publish_start: datetime | None,
        publish_end: datetime | None,
        created_by: str,
    ) -> Announcement:
        start = publish_start or datetime.utcnow()
        end = publish_end or (start + timedelta(days=30))

        ann = Announcement(
            title=title.strip(),
            content=content.strip(),
            importance=importance,
            status=status,
            publish_start=start,
            publish_end=end,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(ann)
        db.commit()
        db.refresh(ann)
        return ann

    @staticmethod
    def update(
        db: Session,
        ann: Announcement,
        title: str,
        content: str,
        importance: str,
        status: str,
        publish_start: datetime | None,
        publish_end: datetime | None,
    ) -> Announcement:
        start = publish_start or ann.publish_start
        end = publish_end or ann.publish_end

        ann.title = title.strip()
        ann.content = content.strip()
        ann.importance = importance
        ann.status = status
        ann.publish_start = start
        ann.publish_end = end
        ann.updated_at = datetime.utcnow()
        db.add(ann)
        db.commit()
        db.refresh(ann)
        return ann

    @staticmethod
    def delete(db: Session, announcement_id: int) -> bool:
        ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not ann:
            return False
        db.delete(ann)
        db.commit()
        return True
