from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment
from app.services.appointment_service import AppointmentService
from app.services.auth_service import get_current_user, require_authenticated_user, user_can_manage_site

router = APIRouter(prefix="/appointments", tags=["appointments"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/book", response_class=HTMLResponse)
def appointment_form(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return templates.TemplateResponse(
        "appointments/book.html",
        {
            "request": request,
            "user": user,
            "error": "",
            "success": "",
        },
    )


@router.post("/book", response_class=HTMLResponse)
def appointment_submit(
    request: Request,
    reason: str = Form(...),
    notes: str = Form(""),
    appointment_time: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    try:
        dt = datetime.fromisoformat(appointment_time)
    except ValueError:
        return templates.TemplateResponse(
            "appointments/book.html",
            {
                "request": request,
                "user": user,
                "error": "Invalid date and time.",
                "success": "",
            },
            status_code=400,
        )

    AppointmentService.create_appointment(
        db,
        patient_id=user.id,
        reason=reason,
        notes=notes,
        appointment_time=dt,
    )
    return templates.TemplateResponse(
        "appointments/book.html",
        {
            "request": request,
            "user": user,
            "error": "",
            "success": "Appointment request submitted.",
        },
    )


@router.get("/my", response_class=HTMLResponse)
def my_appointments(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == user.id)
        .order_by(Appointment.appointment_time.desc())
        .all()
    )
    return templates.TemplateResponse(
        "appointments/my.html",
        {
            "request": request,
            "user": user,
            "appointments": appointments,
        },
    )


@router.get("/manage", response_class=HTMLResponse)
def manage_appointments(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)
    appointments = db.query(Appointment).order_by(Appointment.appointment_time.desc()).all()
    return templates.TemplateResponse(
        "appointments/manage.html",
        {
            "request": request,
            "user": user,
            "appointments": appointments,
        },
    )


@router.post("/{appointment_id}/status")
def update_status(
    appointment_id: int,
    request: Request,
    status_value: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/dashboard", status_code=303)

    AppointmentService.set_status(db, appointment_id=appointment_id, status=status_value)
    return RedirectResponse(url="/appointments/manage", status_code=303)
