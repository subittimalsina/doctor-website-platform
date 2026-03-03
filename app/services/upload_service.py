from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models import AssetUpload

UPLOAD_ROOT = Path("app/static/uploads")
ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".zip",
    ".html",
    ".css",
    ".js",
}


class UploadService:
    def __init__(self):
        UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        base = Path(filename).name
        return "".join(ch for ch in base if ch.isalnum() or ch in {".", "_", "-"}) or "file"

    def _get_subdir(self, filename: str) -> Path:
        ext = Path(filename).suffix.lower()
        mapping = {
            "images": {".png", ".jpg", ".jpeg", ".gif", ".svg"},
            "documents": {".pdf", ".doc", ".docx", ".txt"},
            "website": {".zip", ".html", ".css", ".js"},
        }
        for folder, exts in mapping.items():
            if ext in exts:
                return UPLOAD_ROOT / folder
        return UPLOAD_ROOT / "others"

    def validate_extension(self, filename: str) -> None:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type {ext} is not allowed")

    async def save_upload(self, db: Session, file: UploadFile, uploaded_by: str) -> AssetUpload:
        self.validate_extension(file.filename)
        clean_name = self._sanitize_filename(file.filename)
        ext = Path(clean_name).suffix
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_name = f"{stamp}_{uuid4().hex[:8]}{ext}"

        subdir = self._get_subdir(clean_name)
        subdir.mkdir(parents=True, exist_ok=True)

        target = subdir / unique_name
        content = await file.read()
        with open(target, "wb") as output:
            output.write(content)

        stored_path = str(target.relative_to("app/static"))
        record = AssetUpload(
            filename=clean_name,
            stored_path=stored_path,
            file_type=ext.replace(".", "") or "generic",
            uploaded_by=uploaded_by,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_uploads(self, db: Session) -> list[AssetUpload]:
        return db.query(AssetUpload).order_by(AssetUpload.uploaded_at.desc()).all()

    def delete_upload(self, db: Session, upload_id: int) -> bool:
        record = db.query(AssetUpload).filter(AssetUpload.id == upload_id).first()
        if not record:
            return False

        file_path = Path("app/static") / record.stored_path
        if file_path.exists() and file_path.is_file():
            os.remove(file_path)

        db.delete(record)
        db.commit()
        return True
