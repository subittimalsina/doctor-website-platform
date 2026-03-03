from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RefillRequest
from app.services.auth_service import require_authenticated_user, user_can_manage_site
from app.services.notification_service import NotificationService
from app.services.refill_service import RefillService

router = APIRouter(prefix="/refills", tags=["refills"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/new", response_class=HTMLResponse)
def new_refill_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return templates.TemplateResponse(
        "refills/new.html",
        {
            "request": request,
            "user": user,
            "error": "",
            "success": "",
        },
    )


@router.post("/new", response_class=HTMLResponse)
def create_refill_request(
    request: Request,
    medication_name: str = Form(...),
    dosage: str = Form(""),
    current_supply_days: int = Form(0),
    pharmacy_name: str = Form(""),
    pharmacy_phone: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if len(medication_name.strip()) < 2:
        return templates.TemplateResponse(
            "refills/new.html",
            {
                "request": request,
                "user": user,
                "error": "Medication name is required.",
                "success": "",
            },
            status_code=400,
        )

    req = RefillService.create_request(
        db,
        patient_id=user.id,
        medication_name=medication_name,
        dosage=dosage,
        current_supply_days=max(current_supply_days, 0),
        pharmacy_name=pharmacy_name,
        pharmacy_phone=pharmacy_phone,
        notes=notes,
    )

    NotificationService.send(
        db,
        user_id=user.id,
        title="Refill Request Submitted",
        message=f"Request #{req.id} for {req.medication_name} has been submitted.",
        kind="refill",
    )

    return templates.TemplateResponse(
        "refills/new.html",
        {
            "request": request,
            "user": user,
            "error": "",
            "success": "Refill request submitted successfully.",
        },
    )


@router.get("/my", response_class=HTMLResponse)
def my_refills(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    refills = RefillService.list_for_patient(db, patient_id=user.id)
    return templates.TemplateResponse(
        "refills/my.html",
        {
            "request": request,
            "user": user,
            "refills": refills,
        },
    )


@router.get("/{refill_id}", response_class=HTMLResponse)
def refill_detail(
    refill_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    refill = db.query(RefillRequest).filter(RefillRequest.id == refill_id).first()
    if not refill:
        return RedirectResponse(url="/refills/my", status_code=303)

    if refill.patient_id != user.id and not user_can_manage_site(user):
        return RedirectResponse(url="/refills/my", status_code=303)

    return templates.TemplateResponse(
        "refills/detail.html",
        {
            "request": request,
            "user": user,
            "refill": refill,
        },
    )


@router.get("/manage/all", response_class=HTMLResponse)
def manage_refills(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/refills/my", status_code=303)

    refills = RefillService.list_all(db)
    return templates.TemplateResponse(
        "refills/manage.html",
        {
            "request": request,
            "user": user,
            "refills": refills,
        },
    )


@router.post("/{refill_id}/status")
def update_refill_status(
    refill_id: int,
    request: Request,
    status_value: str = Form(...),
    decision_note: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    refill = db.query(RefillRequest).filter(RefillRequest.id == refill_id).first()
    if not refill:
        return RedirectResponse(url="/refills/manage/all", status_code=303)

    if not user_can_manage_site(user):
        return RedirectResponse(url="/refills/my", status_code=303)

    RefillService.set_status(
        db,
        refill=refill,
        status=status_value,
        reviewed_by=user.email,
        decision_note=decision_note,
    )

    NotificationService.send(
        db,
        user_id=refill.patient_id,
        title="Refill Request Updated",
        message=f"Your refill request #{refill.id} is now marked as {status_value}.",
        kind="refill",
    )

    ref = request.headers.get("referer") or "/refills/manage/all"
    return RedirectResponse(url=ref, status_code=303)
