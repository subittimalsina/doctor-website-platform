from app.database import SessionLocal
from app.models import User


def test_register_login_and_dashboard_flow(client):
    email = "pytest-user@example.com"

    db = SessionLocal()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    register = client.post(
        "/auth/register",
        data={
            "email": email,
            "full_name": "Pytest User",
            "password": "Secret123!",
            "confirm_password": "Secret123!",
        },
        follow_redirects=False,
    )
    assert register.status_code == 303
    assert register.headers["location"] == "/dashboard"

    logout = client.get("/auth/logout", follow_redirects=False)
    assert logout.status_code == 303

    login = client.post(
        "/auth/login",
        data={"email": email, "password": "Secret123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303
    assert login.headers["location"] == "/dashboard"
