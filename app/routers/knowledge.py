from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.knowledge_service import KnowledgeService

router = APIRouter(tags=["knowledge"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/blog", response_class=HTMLResponse)
def blog_index(request: Request, db: Session = Depends(get_db)):
    posts = KnowledgeService.list_posts(db, published_only=True)
    return templates.TemplateResponse(
        "knowledge/blog_list.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "posts": posts,
        },
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
def blog_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    post = KnowledgeService.get_post_by_slug(db, slug)
    if not post or post.is_published != "yes":
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
                "user": get_current_user(request, db),
                "slug": f"blog/{slug}",
            },
            status_code=404,
        )
    return templates.TemplateResponse(
        "knowledge/blog_detail.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "post": post,
        },
    )


@router.get("/faq", response_class=HTMLResponse)
def faq_page(request: Request, db: Session = Depends(get_db)):
    faqs = KnowledgeService.list_faqs(db, published_only=True)
    return templates.TemplateResponse(
        "knowledge/faq.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "faqs": faqs,
        },
    )
