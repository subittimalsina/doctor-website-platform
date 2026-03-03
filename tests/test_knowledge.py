from app.database import SessionLocal
from app.models import BlogPost, FAQItem


def ensure_knowledge():
    db = SessionLocal()
    try:
        post = db.query(BlogPost).filter(BlogPost.slug == "pytest-blog").first()
        if not post:
            db.add(
                BlogPost(
                    slug="pytest-blog",
                    title="Pytest Blog",
                    excerpt="Pytest excerpt",
                    body="<p>Pytest body</p>",
                    author="Test",
                    tags="test",
                    is_published="yes",
                )
            )
        faq = db.query(FAQItem).filter(FAQItem.question == "Pytest FAQ?").first()
        if not faq:
            db.add(
                FAQItem(
                    question="Pytest FAQ?",
                    answer="Pytest answer",
                    category="test",
                    order_index=100,
                    is_published="yes",
                )
            )
        db.commit()
    finally:
        db.close()


def test_blog_and_faq_pages(client):
    ensure_knowledge()

    blog = client.get("/blog")
    assert blog.status_code == 200
    assert "Pytest Blog" in blog.text

    detail = client.get("/blog/pytest-blog")
    assert detail.status_code == 200
    assert "Pytest body" in detail.text

    faq = client.get("/faq")
    assert faq.status_code == 200
    assert "Pytest FAQ" in faq.text
