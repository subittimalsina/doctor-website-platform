from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Announcement
from app.services.announcement_service import AnnouncementService
from app.services.auth_service import get_current_user, require_authenticated_user, user_can_manage_site

router = APIRouter(tags=["announcements"])
templates = Jinja2Templates(directory="app/templates")


def _parse_dt(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


@router.get("/announcements", response_class=HTMLResponse)
def announcement_list(request: Request, db: Session = Depends(get_db)):
    announcements = AnnouncementService.list_published(db)
    return templates.TemplateResponse(
        "announcements/list.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "announcements": announcements,
        },
    )


@router.get("/admin/announcements", response_class=HTMLResponse)
def manage_announcements(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    announcements = AnnouncementService.list_all(db)
    return templates.TemplateResponse(
        "admin/announcements.html",
        {
            "request": request,
            "user": user,
            "announcements": announcements,
            "error": "",
        },
    )


@router.post("/admin/announcements/create", response_class=HTMLResponse)
def create_announcement(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    importance: str = Form("normal"),
    status: str = Form("published"),
    publish_start: str = Form(""),
    publish_end: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    if len(title.strip()) < 4 or len(content.strip()) < 10:
        announcements = AnnouncementService.list_all(db)
        return templates.TemplateResponse(
            "admin/announcements.html",
            {
                "request": request,
                "user": user,
                "announcements": announcements,
                "error": "Title/content are too short.",
            },
            status_code=400,
        )

    start = _parse_dt(publish_start)
    end = _parse_dt(publish_end)
    if start and end and end < start:
        announcements = AnnouncementService.list_all(db)
        return templates.TemplateResponse(
            "admin/announcements.html",
            {
                "request": request,
                "user": user,
                "announcements": announcements,
                "error": "Publish end cannot be earlier than publish start.",
            },
            status_code=400,
        )

    AnnouncementService.create(
        db,
        title=title,
        content=content,
        importance=importance,
        status=status,
        publish_start=start,
        publish_end=end,
        created_by=user.email,
    )
    return RedirectResponse(url="/admin/announcements", status_code=303)


@router.post("/admin/announcements/{announcement_id}/update")
def update_announcement(
    announcement_id: int,
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    importance: str = Form("normal"),
    status: str = Form("published"),
    publish_start: str = Form(""),
    publish_end: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        return RedirectResponse(url="/admin/announcements", status_code=303)

    start = _parse_dt(publish_start)
    end = _parse_dt(publish_end)
    if start and end and end < start:
        return RedirectResponse(url="/admin/announcements", status_code=303)

    AnnouncementService.update(
        db,
        ann=ann,
        title=title,
        content=content,
        importance=importance,
        status=status,
        publish_start=start,
        publish_end=end,
    )
    return RedirectResponse(url="/admin/announcements", status_code=303)


@router.post("/admin/announcements/{announcement_id}/delete")
def delete_announcement(
    announcement_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    AnnouncementService.delete(db, announcement_id=announcement_id)
    return RedirectResponse(url="/admin/announcements", status_code=303)
