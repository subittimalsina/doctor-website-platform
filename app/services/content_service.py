from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CMSPage


class ContentService:
    @staticmethod
    def list_pages(db: Session) -> list[CMSPage]:
        return db.query(CMSPage).order_by(CMSPage.updated_at.desc()).all()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> CMSPage | None:
        return db.query(CMSPage).filter(CMSPage.slug == slug).first()

    @staticmethod
    def create_page(db: Session, slug: str, title: str, summary: str, body: str, is_published: str = "yes") -> CMSPage:
        page = CMSPage(
            slug=slug.strip().lower().replace(" ", "-"),
            title=title.strip(),
            summary=summary.strip(),
            body=body,
            is_published=is_published,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        return page

    @staticmethod
    def update_page(
        db: Session,
        page: CMSPage,
        title: str,
        summary: str,
        body: str,
        is_published: str,
    ) -> CMSPage:
        page.title = title.strip()
        page.summary = summary.strip()
        page.body = body
        page.is_published = is_published
        page.updated_at = datetime.utcnow()
        db.add(page)
        db.commit()
        db.refresh(page)
        return page

    @staticmethod
    def delete_page(db: Session, page_id: int) -> bool:
        page = db.query(CMSPage).filter(CMSPage.id == page_id).first()
        if not page:
            return False
        db.delete(page)
        db.commit()
        return True
