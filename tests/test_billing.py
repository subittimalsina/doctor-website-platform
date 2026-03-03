from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService


def ensure_accounts():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "billing-admin@example.com").first()
        patient = db.query(User).filter(User.email == "billing-patient@example.com").first()
        if not admin:
            admin = AuthService.create_user(
                db,
                email="billing-admin@example.com",
                full_name="Billing Admin",
                password="AdminPass123!",
                role="admin",
            )
        if not patient:
            patient = AuthService.create_user(
                db,
                email="billing-patient@example.com",
                full_name="Billing Patient",
                password="PatientPass123!",
                role="patient",
            )
        return patient.id
    finally:
        db.close()


def test_billing_create_invoice(client):
    patient_id = ensure_accounts()

    login = client.post(
        "/auth/login",
        data={"email": "billing-admin@example.com", "password": "AdminPass123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    response = client.post(
        "/billing/manage/create",
        data={
            "patient_id": patient_id,
            "description": "Pytest invoice",
            "amount": "99.99",
            "due_days": 7,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/billing/manage"
