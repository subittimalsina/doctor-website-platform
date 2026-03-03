from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import require_authenticated_user
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def notification_list(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    notifications = NotificationService.list_for_user(db, user_id=user.id)
    return templates.TemplateResponse(
        "notifications/list.html",
        {
            "request": request,
            "user": user,
            "notifications": notifications,
        },
    )


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    NotificationService.mark_read(db, notification_id=notification_id, user_id=user.id)
    ref = request.headers.get("referer") or "/notifications"
    return RedirectResponse(url=ref, status_code=303)
