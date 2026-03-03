from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService


def ensure_test_user():
    db = SessionLocal()
    try:
        email = "support-test@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = AuthService.create_user(
                db,
                email=email,
                full_name="Support User",
                password="Secret123!",
                role="patient",
            )
        return email
    finally:
        db.close()


def test_create_support_ticket(client):
    email = ensure_test_user()

    login = client.post(
        "/auth/login",
        data={"email": email, "password": "Secret123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    create = client.post(
        "/support/new",
        data={
            "subject": "Portal help",
            "category": "general",
            "priority": "normal",
            "message": "I need help changing appointment time.",
        },
    )
    assert create.status_code == 200
    assert "Support ticket created" in create.text
