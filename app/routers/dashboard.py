from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, SupportTicket
from app.services.auth_service import require_authenticated_user, user_can_manage_site

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def user_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if user_can_manage_site(user):
        return RedirectResponse(url="/admin", status_code=303)

    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == user.id)
        .order_by(Appointment.appointment_time.desc())
        .limit(5)
        .all()
    )
    tickets = (
        db.query(SupportTicket)
        .filter(SupportTicket.user_id == user.id)
        .order_by(SupportTicket.updated_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "appointments": appointments,
            "tickets": tickets,
        },
    )
