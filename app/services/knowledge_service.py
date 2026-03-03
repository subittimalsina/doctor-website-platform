from datetime import datetime

from sqlalchemy.orm import Session

from app.models import BlogPost, FAQItem


class KnowledgeService:
    @staticmethod
    def list_posts(db: Session, published_only: bool = True) -> list[BlogPost]:
        query = db.query(BlogPost)
        if published_only:
            query = query.filter(BlogPost.is_published == "yes")
        return query.order_by(BlogPost.created_at.desc()).all()

    @staticmethod
    def get_post_by_slug(db: Session, slug: str) -> BlogPost | None:
        return db.query(BlogPost).filter(BlogPost.slug == slug).first()

    @staticmethod
    def create_post(
        db: Session,
        slug: str,
        title: str,
        excerpt: str,
        body: str,
        author: str,
        tags: str,
        is_published: str,
    ) -> BlogPost:
        post = BlogPost(
            slug=slug.strip().lower().replace(" ", "-"),
            title=title.strip(),
            excerpt=excerpt.strip(),
            body=body,
            author=author,
            tags=tags,
            is_published=is_published,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def update_post(
        db: Session,
        post: BlogPost,
        title: str,
        excerpt: str,
        body: str,
        author: str,
        tags: str,
        is_published: str,
    ) -> BlogPost:
        post.title = title.strip()
        post.excerpt = excerpt.strip()
        post.body = body
        post.author = author.strip()
        post.tags = tags.strip()
        post.is_published = is_published
        post.updated_at = datetime.utcnow()
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def delete_post(db: Session, post_id: int) -> bool:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        if not post:
            return False
        db.delete(post)
        db.commit()
        return True

    @staticmethod
    def list_faqs(db: Session, published_only: bool = True) -> list[FAQItem]:
        query = db.query(FAQItem)
        if published_only:
            query = query.filter(FAQItem.is_published == "yes")
        return query.order_by(FAQItem.order_index.asc(), FAQItem.id.asc()).all()

    @staticmethod
    def create_faq(db: Session, question: str, answer: str, category: str, order_index: int, is_published: str) -> FAQItem:
        faq = FAQItem(
            question=question.strip(),
            answer=answer.strip(),
            category=category,
            order_index=order_index,
            is_published=is_published,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq

    @staticmethod
    def update_faq(
        db: Session,
        faq: FAQItem,
        question: str,
        answer: str,
        category: str,
        order_index: int,
        is_published: str,
    ) -> FAQItem:
        faq.question = question.strip()
        faq.answer = answer.strip()
        faq.category = category
        faq.order_index = order_index
        faq.is_published = is_published
        faq.updated_at = datetime.utcnow()
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq

    @staticmethod
    def delete_faq(db: Session, faq_id: int) -> bool:
        faq = db.query(FAQItem).filter(FAQItem.id == faq_id).first()
        if not faq:
            return False
        db.delete(faq)
        db.commit()
        return True
