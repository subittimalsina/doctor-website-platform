from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BlogPost, ContactLead, FAQItem
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.services.auth_service import require_authenticated_user, user_can_manage_site
from app.services.contact_service import ContactService
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/admin", tags=["operations"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/reports", response_class=HTMLResponse)
def reports(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    metrics = AnalyticsService.global_metrics(db)
    breakdown = AnalyticsService.status_breakdown(db)
    logs = AuditService.recent(db, limit=40)
    return templates.TemplateResponse(
        "admin/reports.html",
        {
            "request": request,
            "user": user,
            "metrics": metrics,
            "breakdown": breakdown,
            "logs": logs,
        },
    )


@router.get("/blog", response_class=HTMLResponse)
def manage_blog(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    posts = KnowledgeService.list_posts(db, published_only=False)
    return templates.TemplateResponse(
        "admin/blog.html",
        {
            "request": request,
            "user": user,
            "posts": posts,
            "error": "",
        },
    )


@router.post("/blog/create")
def create_blog(
    request: Request,
    slug: str = Form(...),
    title: str = Form(...),
    excerpt: str = Form(""),
    body: str = Form(""),
    author: str = Form("Doctor Team"),
    tags: str = Form("general"),
    is_published: str = Form("yes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    exists = KnowledgeService.get_post_by_slug(db, slug)
    if exists:
        posts = KnowledgeService.list_posts(db, published_only=False)
        return templates.TemplateResponse(
            "admin/blog.html",
            {
                "request": request,
                "user": user,
                "posts": posts,
                "error": "Slug already used by another post.",
            },
            status_code=400,
        )

    post = KnowledgeService.create_post(
        db,
        slug=slug,
        title=title,
        excerpt=excerpt,
        body=body,
        author=author,
        tags=tags,
        is_published=is_published,
    )
    AuditService.log(db, actor_email=user.email, action="blog.create", target_type="BlogPost", target_id=post.id)
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/blog/{post_id}/update")
def update_blog(
    post_id: int,
    request: Request,
    title: str = Form(...),
    excerpt: str = Form(""),
    body: str = Form(""),
    author: str = Form("Doctor Team"),
    tags: str = Form("general"),
    is_published: str = Form("yes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        return RedirectResponse(url="/admin/blog", status_code=303)

    KnowledgeService.update_post(
        db,
        post=post,
        title=title,
        excerpt=excerpt,
        body=body,
        author=author,
        tags=tags,
        is_published=is_published,
    )
    AuditService.log(db, actor_email=user.email, action="blog.update", target_type="BlogPost", target_id=post.id)
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/blog/{post_id}/delete")
def delete_blog(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    KnowledgeService.delete_post(db, post_id)
    AuditService.log(db, actor_email=user.email, action="blog.delete", target_type="BlogPost", target_id=post_id)
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.get("/faq", response_class=HTMLResponse)
def manage_faq(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    faqs = KnowledgeService.list_faqs(db, published_only=False)
    return templates.TemplateResponse(
        "admin/faq.html",
        {
            "request": request,
            "user": user,
            "faqs": faqs,
        },
    )


@router.post("/faq/create")
def create_faq(
    question: str = Form(...),
    answer: str = Form(...),
    category: str = Form("general"),
    order_index: int = Form(0),
    is_published: str = Form("yes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    faq = KnowledgeService.create_faq(
        db,
        question=question,
        answer=answer,
        category=category,
        order_index=order_index,
        is_published=is_published,
    )
    AuditService.log(db, actor_email=user.email, action="faq.create", target_type="FAQItem", target_id=faq.id)
    return RedirectResponse(url="/admin/faq", status_code=303)


@router.post("/faq/{faq_id}/update")
def update_faq(
    faq_id: int,
    question: str = Form(...),
    answer: str = Form(...),
    category: str = Form("general"),
    order_index: int = Form(0),
    is_published: str = Form("yes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    faq = db.query(FAQItem).filter(FAQItem.id == faq_id).first()
    if not faq:
        return RedirectResponse(url="/admin/faq", status_code=303)

    KnowledgeService.update_faq(
        db,
        faq=faq,
        question=question,
        answer=answer,
        category=category,
        order_index=order_index,
        is_published=is_published,
    )
    AuditService.log(db, actor_email=user.email, action="faq.update", target_type="FAQItem", target_id=faq.id)
    return RedirectResponse(url="/admin/faq", status_code=303)


@router.post("/faq/{faq_id}/delete")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    KnowledgeService.delete_faq(db, faq_id)
    AuditService.log(db, actor_email=user.email, action="faq.delete", target_type="FAQItem", target_id=faq_id)
    return RedirectResponse(url="/admin/faq", status_code=303)


@router.get("/leads", response_class=HTMLResponse)
def manage_leads(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    leads = ContactService.list_leads(db)
    return templates.TemplateResponse(
        "admin/leads.html",
        {
            "request": request,
            "user": user,
            "leads": leads,
        },
    )


@router.post("/leads/{lead_id}/status")
def update_lead_status(
    lead_id: int,
    status_value: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    ContactService.set_status(db, lead_id=lead_id, status=status_value)
    AuditService.log(db, actor_email=user.email, action="lead.status", target_type="ContactLead", target_id=lead_id)
    return RedirectResponse(url="/admin/leads", status_code=303)
