from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService
from app.services.notification_service import NotificationService


def ensure_user_and_notification():
    db = SessionLocal()
    try:
        email = "notification-user@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = AuthService.create_user(
                db,
                email=email,
                full_name="Notification User",
                password="Secret123!",
                role="patient",
            )
        NotificationService.send(
            db,
            user_id=user.id,
            title="Test Notification",
            message="Notification body",
            kind="system",
        )
        return email
    finally:
        db.close()


def test_notifications_page(client):
    email = ensure_user_and_notification()
    login = client.post(
        "/auth/login",
        data={"email": email, "password": "Secret123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    page = client.get("/notifications")
    assert page.status_code == 200
    assert "Test Notification" in page.text
