from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, BlogPost, CMSPage, ContactLead, FAQItem, Invoice, SupportTicket, User
from app.services.auth_service import get_current_user, require_authenticated_user, user_can_manage_site
from app.services.content_service import ContentService
from app.services.upload_service import UploadService

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")
upload_service = UploadService()


@router.get("", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    stats = {
        "patients": db.query(User).filter(User.role == "patient").count(),
        "appointments": db.query(Appointment).count(),
        "tickets": db.query(SupportTicket).count(),
        "pages": len(ContentService.list_pages(db)),
        "invoices": db.query(Invoice).count(),
        "blog_posts": db.query(BlogPost).count(),
        "faqs": db.query(FAQItem).count(),
        "leads": db.query(ContactLead).count(),
    }
    recent_appointments = db.query(Appointment).order_by(Appointment.created_at.desc()).limit(8).all()
    recent_tickets = db.query(SupportTicket).order_by(SupportTicket.updated_at.desc()).limit(8).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "recent_appointments": recent_appointments,
            "recent_tickets": recent_tickets,
        },
    )


@router.get("/pages", response_class=HTMLResponse)
def page_list(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    pages = ContentService.list_pages(db)
    return templates.TemplateResponse(
        "admin/pages.html",
        {
            "request": request,
            "user": user,
            "pages": pages,
            "error": "",
        },
    )


@router.post("/pages/create")
def page_create(
    request: Request,
    slug: str = Form(...),
    title: str = Form(...),
    summary: str = Form(""),
    body: str = Form(""),
    is_published: str = Form("yes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    existing = ContentService.get_by_slug(db, slug)
    if existing:
        pages = ContentService.list_pages(db)
        return templates.TemplateResponse(
            "admin/pages.html",
            {
                "request": request,
                "user": user,
                "pages": pages,
                "error": "A page with this slug already exists.",
            },
            status_code=400,
        )

    ContentService.create_page(
        db,
        slug=slug,
        title=title,
        summary=summary,
        body=body,
        is_published=is_published,
    )
    return RedirectResponse(url="/admin/pages", status_code=303)


@router.post("/pages/{page_id}/update")
def page_update(
    page_id: int,
    request: Request,
    title: str = Form(...),
    summary: str = Form(""),
    body: str = Form(""),
    is_published: str = Form("yes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    page = db.query(CMSPage).filter(CMSPage.id == page_id).first()
    if not page:
        return RedirectResponse(url="/admin/pages", status_code=303)

    ContentService.update_page(db, page=page, title=title, summary=summary, body=body, is_published=is_published)
    return RedirectResponse(url="/admin/pages", status_code=303)


@router.post("/pages/{page_id}/delete")
def page_delete(
    page_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    ContentService.delete_page(db, page_id)
    return RedirectResponse(url="/admin/pages", status_code=303)


@router.get("/uploads", response_class=HTMLResponse)
def uploads_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    uploads = upload_service.list_uploads(db)
    return templates.TemplateResponse(
        "admin/uploads.html",
        {
            "request": request,
            "user": user,
            "uploads": uploads,
            "error": "",
            "success": "",
        },
    )


@router.post("/uploads")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    try:
        await upload_service.save_upload(db, file=file, uploaded_by=user.email)
    except ValueError as exc:
        uploads = upload_service.list_uploads(db)
        return templates.TemplateResponse(
            "admin/uploads.html",
            {
                "request": request,
                "user": user,
                "uploads": uploads,
                "error": str(exc),
                "success": "",
            },
            status_code=400,
        )

    return RedirectResponse(url="/admin/uploads", status_code=303)


@router.post("/uploads/{upload_id}/delete")
def delete_upload(
    upload_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    upload_service.delete_upload(db, upload_id=upload_id)
    return RedirectResponse(url="/admin/uploads", status_code=303)
