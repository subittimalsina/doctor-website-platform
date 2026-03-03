from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Invoice, User
from app.services.auth_service import require_authenticated_user, user_can_manage_site
from app.services.billing_service import BillingService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/billing", tags=["billing"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/my", response_class=HTMLResponse)
def my_invoices(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == user.id)
        .order_by(Invoice.issued_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "billing/my.html",
        {
            "request": request,
            "user": user,
            "invoices": invoices,
        },
    )


@router.get("/manage", response_class=HTMLResponse)
def manage_invoices(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/billing/my", status_code=303)

    invoices = db.query(Invoice).order_by(Invoice.issued_at.desc()).all()
    patients = db.query(User).filter(User.role == "patient").order_by(User.full_name.asc()).all()
    return templates.TemplateResponse(
        "billing/manage.html",
        {
            "request": request,
            "user": user,
            "invoices": invoices,
            "patients": patients,
            "error": "",
        },
    )


@router.post("/manage/create", response_class=HTMLResponse)
def create_invoice(
    request: Request,
    patient_id: int = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    due_days: int = Form(14),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/billing/my", status_code=303)

    if amount <= 0:
        invoices = db.query(Invoice).order_by(Invoice.issued_at.desc()).all()
        patients = db.query(User).filter(User.role == "patient").order_by(User.full_name.asc()).all()
        return templates.TemplateResponse(
            "billing/manage.html",
            {
                "request": request,
                "user": user,
                "invoices": invoices,
                "patients": patients,
                "error": "Amount must be positive.",
            },
            status_code=400,
        )

    invoice = BillingService.create_invoice(
        db,
        user_id=patient_id,
        description=description,
        amount=amount,
        due_days=due_days,
    )
    NotificationService.send(
        db,
        user_id=patient_id,
        title="New Invoice Issued",
        message=f"Invoice {invoice.invoice_number} for ${float(invoice.amount):.2f} is now available.",
        kind="billing",
    )
    return RedirectResponse(url="/billing/manage", status_code=303)


@router.post("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: int,
    request: Request,
    status_value: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/billing/my", status_code=303)

    ok = BillingService.mark_invoice_status(db, invoice_id=invoice_id, status=status_value, note=note)
    if ok:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            NotificationService.send(
                db,
                user_id=invoice.user_id,
                title=f"Invoice {invoice.invoice_number} Updated",
                message=f"Invoice status changed to {status_value}.",
                kind="billing",
            )

    return RedirectResponse(url="/billing/manage", status_code=303)
