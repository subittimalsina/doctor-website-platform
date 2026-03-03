from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MedicalRecord, Prescription, User
from app.services.auth_service import require_authenticated_user, user_can_manage_site
from app.services.notification_service import NotificationService
from app.services.record_service import RecordService

router = APIRouter(prefix="/records", tags=["records"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/my", response_class=HTMLResponse)
def my_records(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == user.id)
        .order_by(MedicalRecord.updated_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "records/my.html",
        {
            "request": request,
            "user": user,
            "records": records,
        },
    )


@router.get("/{record_id}", response_class=HTMLResponse)
def record_detail(
    record_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        return RedirectResponse(url="/records/my", status_code=303)

    if record.patient_id != user.id and not user_can_manage_site(user):
        return RedirectResponse(url="/records/my", status_code=303)

    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.record_id == record.id)
        .order_by(Prescription.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "records/detail.html",
        {
            "request": request,
            "user": user,
            "record": record,
            "prescriptions": prescriptions,
        },
    )


@router.get("/manage", response_class=HTMLResponse)
def manage_records(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/records/my", status_code=303)

    records = db.query(MedicalRecord).order_by(MedicalRecord.updated_at.desc()).all()
    patients = db.query(User).filter(User.role == "patient").order_by(User.full_name.asc()).all()
    return templates.TemplateResponse(
        "records/manage.html",
        {
            "request": request,
            "user": user,
            "records": records,
            "patients": patients,
            "error": "",
        },
    )


@router.post("/manage/create", response_class=HTMLResponse)
def create_record(
    request: Request,
    patient_id: int = Form(...),
    record_title: str = Form(...),
    diagnosis_summary: str = Form(""),
    observations: str = Form(""),
    recommendations: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/records/my", status_code=303)

    if len(record_title.strip()) < 4:
        records = db.query(MedicalRecord).order_by(MedicalRecord.updated_at.desc()).all()
        patients = db.query(User).filter(User.role == "patient").order_by(User.full_name.asc()).all()
        return templates.TemplateResponse(
            "records/manage.html",
            {
                "request": request,
                "user": user,
                "records": records,
                "patients": patients,
                "error": "Record title must be at least 4 characters.",
            },
            status_code=400,
        )

    record = RecordService.create_record(
        db,
        patient_id=patient_id,
        record_title=record_title,
        diagnosis_summary=diagnosis_summary,
        observations=observations,
        recommendations=recommendations,
        created_by=user.email,
    )
    NotificationService.send(
        db,
        user_id=patient_id,
        title="New Medical Record Added",
        message=f"A new record '{record.record_title}' has been added to your profile.",
        kind="records",
    )
    return RedirectResponse(url="/records/manage", status_code=303)


@router.post("/{record_id}/update")
def update_record(
    record_id: int,
    request: Request,
    record_title: str = Form(...),
    diagnosis_summary: str = Form(""),
    observations: str = Form(""),
    recommendations: str = Form(""),
    status: str = Form("active"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url=f"/records/{record_id}", status_code=303)

    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        return RedirectResponse(url="/records/manage", status_code=303)

    RecordService.update_record(
        db,
        record=record,
        record_title=record_title,
        diagnosis_summary=diagnosis_summary,
        observations=observations,
        recommendations=recommendations,
        status=status,
    )
    return RedirectResponse(url="/records/manage", status_code=303)


@router.post("/{record_id}/delete")
def delete_record(
    record_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    if not user_can_manage_site(user):
        return RedirectResponse(url="/records/my", status_code=303)
    RecordService.delete_record(db, record_id=record_id)
    return RedirectResponse(url="/records/manage", status_code=303)


@router.post("/{record_id}/prescriptions")
def add_prescription(
    record_id: int,
    request: Request,
    medicine_name: str = Form(...),
    dosage: str = Form(""),
    schedule: str = Form(""),
    duration: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        return RedirectResponse(url="/records/manage", status_code=303)

    if record.patient_id != user.id and not user_can_manage_site(user):
        return RedirectResponse(url="/records/my", status_code=303)

    if not user_can_manage_site(user):
        return RedirectResponse(url=f"/records/{record_id}", status_code=303)

    RecordService.add_prescription(
        db,
        record_id=record_id,
        medicine_name=medicine_name,
        dosage=dosage,
        schedule=schedule,
        duration=duration,
        notes=notes,
    )
    NotificationService.send(
        db,
        user_id=record.patient_id,
        title="Prescription Added",
        message=f"A new prescription was added for record '{record.record_title}'.",
        kind="records",
    )
    return RedirectResponse(url=f"/records/{record_id}", status_code=303)


@router.post("/prescriptions/{prescription_id}/delete")
def delete_prescription(
    prescription_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    item = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not item:
        return RedirectResponse(url="/records/manage", status_code=303)

    record = db.query(MedicalRecord).filter(MedicalRecord.id == item.record_id).first()
    if not record:
        return RedirectResponse(url="/records/manage", status_code=303)

    if not user_can_manage_site(user):
        return RedirectResponse(url=f"/records/{record.id}", status_code=303)

    RecordService.delete_prescription(db, prescription_id=prescription_id)
    return RedirectResponse(url=f"/records/{record.id}", status_code=303)
