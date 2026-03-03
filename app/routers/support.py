from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SupportTicket
from app.services.auth_service import get_current_user, require_authenticated_user, user_can_manage_site
from app.services.support_service import SupportService

router = APIRouter(prefix="/support", tags=["support"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/new", response_class=HTMLResponse)
def new_ticket_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return templates.TemplateResponse(
        "support/new.html",
        {
            "request": request,
            "user": user,
            "error": "",
            "success": "",
        },
    )


@router.post("/new", response_class=HTMLResponse)
def create_ticket(
    request: Request,
    subject: str = Form(...),
    category: str = Form("general"),
    priority: str = Form("normal"),
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if len(message.strip()) < 10:
        return templates.TemplateResponse(
            "support/new.html",
            {
                "request": request,
                "user": user,
                "error": "Please provide more detail (minimum 10 chars).",
                "success": "",
            },
            status_code=400,
        )

    SupportService.create_ticket(
        db,
        user_id=user.id,
        subject=subject,
        category=category,
        priority=priority,
        message=message,
    )
    return templates.TemplateResponse(
        "support/new.html",
        {
            "request": request,
            "user": user,
            "error": "",
            "success": "Support ticket created.",
        },
    )


@router.get("/my", response_class=HTMLResponse)
def my_tickets(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    tickets = (
        db.query(SupportTicket)
        .filter(SupportTicket.user_id == user.id)
        .order_by(SupportTicket.updated_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "support/my.html",
        {
            "request": request,
            "user": user,
            "tickets": tickets,
        },
    )


@router.get("/{ticket_id}", response_class=HTMLResponse)
def ticket_detail(
    ticket_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        return RedirectResponse(url="/support/my", status_code=303)

    if ticket.user_id != user.id and not user_can_manage_site(user):
        return RedirectResponse(url="/support/my", status_code=303)

    return templates.TemplateResponse(
        "support/detail.html",
        {
            "request": request,
            "user": user,
            "ticket": ticket,
            "messages": ticket.messages,
        },
    )


@router.post("/{ticket_id}/reply")
def reply_ticket(
    ticket_id: int,
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        return RedirectResponse(url="/support/my", status_code=303)

    if ticket.user_id != user.id and not user_can_manage_site(user):
        return RedirectResponse(url="/support/my", status_code=303)

    sender_role = user.role if user_can_manage_site(user) else "patient"
    SupportService.add_message(db, ticket_id=ticket_id, sender_role=sender_role, message=message)
    return RedirectResponse(url=f"/support/{ticket_id}", status_code=303)


@router.get("/manage/all", response_class=HTMLResponse)
def manage_tickets(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/support/my", status_code=303)

    tickets = db.query(SupportTicket).order_by(SupportTicket.updated_at.desc()).all()
    return templates.TemplateResponse(
        "support/manage.html",
        {
            "request": request,
            "user": user,
            "tickets": tickets,
        },
    )


@router.post("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    request: Request,
    status_value: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/support/my", status_code=303)

    SupportService.change_status(db, ticket_id=ticket_id, status=status_value)
    return RedirectResponse(url="/support/manage/all", status_code=303)
