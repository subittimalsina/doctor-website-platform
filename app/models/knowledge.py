from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    excerpt: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(255), default="Doctor Team")
    tags: Mapped[str] = mapped_column(String(255), default="general")
    is_published: Mapped[str] = mapped_column(String(10), default="yes")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FAQItem(Base):
    __tablename__ = "faq_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[str] = mapped_column(String(10), default="yes")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
