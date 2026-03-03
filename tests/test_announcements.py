from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService


def ensure_admin_user():
    db = SessionLocal()
    try:
        email = "announcement-admin@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = AuthService.create_user(
                db,
                email=email,
                full_name="Announcement Admin",
                password="AdminPass123!",
                role="admin",
            )
        return email
    finally:
        db.close()


def test_create_and_view_announcement(client):
    admin_email = ensure_admin_user()

    login = client.post(
        "/auth/login",
        data={"email": admin_email, "password": "AdminPass123!"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    create = client.post(
        "/admin/announcements/create",
        data={
            "title": "Pytest Announcement",
            "content": "This is an announcement created by automated test.",
            "importance": "high",
            "status": "published",
            "publish_start": "",
            "publish_end": "",
        },
        follow_redirects=False,
    )
    assert create.status_code == 303
    assert create.headers["location"] == "/admin/announcements"

    page = client.get("/announcements")
    assert page.status_code == 200
    assert "Pytest Announcement" in page.text

    api = client.get("/api/announcements")
    assert api.status_code == 200
    data = api.json()
    assert isinstance(data, list)
    assert any(item.get("title") == "Pytest Announcement" for item in data)
