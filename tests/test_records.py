from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService


def ensure_doctor_and_patient():
    db = SessionLocal()
    try:
        doctor = db.query(User).filter(User.email == "records-doctor@example.com").first()
        patient = db.query(User).filter(User.email == "records-patient@example.com").first()

        if not doctor:
            doctor = AuthService.create_user(
                db,
                email="records-doctor@example.com",
                full_name="Records Doctor",
                password="DoctorPass123!",
                role="doctor",
            )
        if not patient:
            patient = AuthService.create_user(
                db,
                email="records-patient@example.com",
                full_name="Records Patient",
                password="PatientPass123!",
                role="patient",
            )
        return patient.id
    finally:
        db.close()


def test_create_record_flow(client):
    patient_id = ensure_doctor_and_patient()

    login = client.post(
        "/auth/login",
        data={"email": "records-doctor@example.com", "password": "DoctorPass123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    create = client.post(
        "/records/manage/create",
        data={
            "patient_id": patient_id,
            "record_title": "Pytest Clinical Record",
            "diagnosis_summary": "Stable",
            "observations": "All good",
            "recommendations": "Continue meds",
        },
        follow_redirects=False,
    )
    assert create.status_code == 303
    assert create.headers["location"] == "/records/manage"
