from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CMSPage(Base):
    __tablename__ = "cms_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    is_published: Mapped[str] = mapped_column(String(10), default="yes")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AssetUpload(Base):
    __tablename__ = "asset_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), default="generic")
    uploaded_by: Mapped[str] = mapped_column(String(255), default="system")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
