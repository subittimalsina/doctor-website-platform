from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService


def ensure_patient():
    db = SessionLocal()
    try:
        email = "refill-patient@example.com"
        patient = db.query(User).filter(User.email == email).first()
        if not patient:
            patient = AuthService.create_user(
                db,
                email=email,
                full_name="Refill Patient",
                password="PatientPass123!",
                role="patient",
            )
        return email
    finally:
        db.close()


def test_refill_request_flow(client):
    email = ensure_patient()

    login = client.post(
        "/auth/login",
        data={"email": email, "password": "PatientPass123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    create = client.post(
        "/refills/new",
        data={
            "medication_name": "Metformin",
            "dosage": "500mg twice daily",
            "current_supply_days": 3,
            "pharmacy_name": "Main Street Pharmacy",
            "pharmacy_phone": "+1-555-888-1000",
            "notes": "Need refill this week",
        },
    )
    assert create.status_code == 200
    assert "submitted successfully" in create.text

    page = client.get("/refills/my")
    assert page.status_code == 200
    assert "Metformin" in page.text

    api = client.get("/api/refills/my")
    assert api.status_code == 200
    data = api.json()
    assert isinstance(data, list)
    assert any(row.get("medication_name") == "Metformin" for row in data)
