from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.contact_service import ContactService
from app.services.content_service import ContentService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    pages = [p for p in ContentService.list_pages(db) if p.is_published == "yes"]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "pages": pages[:6],
        },
    )


@router.get("/about", response_class=HTMLResponse)
def about(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "user": get_current_user(request, db),
        },
    )


@router.get("/services", response_class=HTMLResponse)
def services(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "services.html",
        {
            "request": request,
            "user": get_current_user(request, db),
        },
    )


@router.get("/contact", response_class=HTMLResponse)
def contact(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "success": "",
            "error": "",
        },
    )


@router.post("/contact", response_class=HTMLResponse)
def contact_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    subject: str = Form("General Inquiry"),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if len(message.strip()) < 10:
        return templates.TemplateResponse(
            "contact.html",
            {
                "request": request,
                "user": user,
                "success": "",
                "error": "Please provide more details in your message.",
            },
            status_code=400,
        )

    ContactService.create_lead(
        db,
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "user": user,
            "success": "Your message has been submitted. Our team will contact you soon.",
            "error": "",
        },
    )


@router.get("/page/{slug}", response_class=HTMLResponse)
def cms_page(slug: str, request: Request, db: Session = Depends(get_db)):
    page = ContentService.get_by_slug(db, slug)
    if not page or page.is_published != "yes":
        return templates.TemplateResponse(
            "not_found.html",
            {"request": request, "user": get_current_user(request, db), "slug": slug},
            status_code=404,
        )

    return templates.TemplateResponse(
        "cms/page.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "page": page,
        },
    )
