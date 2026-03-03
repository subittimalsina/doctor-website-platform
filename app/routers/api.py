from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Announcement, Appointment, ContactLead, Invoice, MedicalRecord, RefillRequest, SupportTicket, User
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import require_roles
from app.services.content_service import ContentService
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@router.get("/stats")
def stats(db: Session = Depends(get_db), user=Depends(require_roles("doctor", "admin"))):
    return {
        "users": db.query(User).count(),
        "patients": db.query(User).filter(User.role == "patient").count(),
        "appointments": db.query(Appointment).count(),
        "tickets": db.query(SupportTicket).count(),
        "pages": len(ContentService.list_pages(db)),
        "requested_by": user.email,
    }


@router.get("/pages")
def pages(db: Session = Depends(get_db)):
    pages_data = []
    for page in ContentService.list_pages(db):
        pages_data.append(
            {
                "slug": page.slug,
                "title": page.title,
                "summary": page.summary,
                "published": page.is_published,
                "updated_at": page.updated_at.isoformat(),
            }
        )
    return pages_data


@router.get("/knowledge")
def knowledge(db: Session = Depends(get_db)):
    posts = KnowledgeService.list_posts(db, published_only=True)
    faqs = KnowledgeService.list_faqs(db, published_only=True)
    return {
        "posts": [
            {
                "slug": p.slug,
                "title": p.title,
                "excerpt": p.excerpt,
                "author": p.author,
                "tags": p.tags,
            }
            for p in posts
        ],
        "faqs": [
            {
                "id": f.id,
                "question": f.question,
                "answer": f.answer,
                "category": f.category,
            }
            for f in faqs
        ],
    }


@router.get("/reports/metrics")
def report_metrics(db: Session = Depends(get_db), user=Depends(require_roles("doctor", "admin"))):
    data = AnalyticsService.global_metrics(db)
    data["requested_by"] = user.email
    return data


@router.get("/reports/status")
def report_status(db: Session = Depends(get_db), user=Depends(require_roles("doctor", "admin"))):
    data = AnalyticsService.status_breakdown(db)
    data["requested_by"] = user.email
    return data


@router.get("/counts/public")
def public_counts(db: Session = Depends(get_db)):
    return {
        "appointments": db.query(Appointment).count(),
        "support_tickets": db.query(SupportTicket).count(),
        "refill_requests": db.query(RefillRequest).count(),
        "invoices": db.query(Invoice).count(),
        "contact_leads": db.query(ContactLead).count(),
        "medical_records": db.query(MedicalRecord).count(),
        "announcements": db.query(Announcement).count(),
    }


@router.get("/records/my")
def my_records_api(db: Session = Depends(get_db), user=Depends(require_roles("patient", "doctor", "admin"))):
    query = db.query(MedicalRecord)
    if user.role == "patient":
        query = query.filter(MedicalRecord.patient_id == user.id)
    rows = query.order_by(MedicalRecord.updated_at.desc()).all()
    return [
        {
            "id": r.id,
            "patient_id": r.patient_id,
            "record_title": r.record_title,
            "diagnosis_summary": r.diagnosis_summary,
            "status": r.status,
            "updated_at": r.updated_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/announcements")
def announcements_api(db: Session = Depends(get_db)):
    rows = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return [
        {
            "id": ann.id,
            "title": ann.title,
            "content": ann.content,
            "importance": ann.importance,
            "status": ann.status,
            "publish_start": ann.publish_start.isoformat(),
            "publish_end": ann.publish_end.isoformat(),
            "created_by": ann.created_by,
        }
        for ann in rows
    ]


@router.get("/refills/my")
def my_refills_api(db: Session = Depends(get_db), user=Depends(require_roles("patient", "doctor", "admin"))):
    query = db.query(RefillRequest)
    if user.role == "patient":
        query = query.filter(RefillRequest.patient_id == user.id)
    rows = query.order_by(RefillRequest.updated_at.desc()).all()
    return [
        {
            "id": row.id,
            "patient_id": row.patient_id,
            "medication_name": row.medication_name,
            "dosage": row.dosage,
            "current_supply_days": row.current_supply_days,
            "pharmacy_name": row.pharmacy_name,
            "status": row.status,
            "reviewed_by": row.reviewed_by,
            "updated_at": row.updated_at.isoformat(),
        }
        for row in rows
    ]
