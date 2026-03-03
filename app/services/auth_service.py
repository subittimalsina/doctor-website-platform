from typing import Iterable

from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @classmethod
    def create_user(
        cls,
        db: Session,
        email: str,
        full_name: str,
        password: str,
        role: str = "patient",
    ) -> User:
        existing = cls.get_user_by_email(db, email)
        if existing:
            raise ValueError("Email already registered")
        user = User(
            email=email.lower().strip(),
            full_name=full_name.strip(),
            hashed_password=cls.hash_password(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> User | None:
        user = cls.get_user_by_email(db, email)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def login_user(request: Request, user: User) -> None:
        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
        }

    @staticmethod
    def logout_user(request: Request) -> None:
        request.session.clear()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    session_user = request.session.get("user")
    if not session_user:
        return None
    user_id = session_user.get("id")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    return user


def require_authenticated_user(current_user: User | None = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return current_user


def require_roles(*roles: str):
    allowed = set(roles)

    def dependency(user: User = Depends(require_authenticated_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency


def user_can_manage_site(user: User) -> bool:
    return user.role in {"doctor", "admin"}


def list_roles() -> Iterable[str]:
    return ["patient", "doctor", "admin"]
