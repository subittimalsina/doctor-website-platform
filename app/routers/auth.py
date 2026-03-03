from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "error": "",
        },
    )


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "user": get_current_user(request, db),
                "error": "Passwords do not match.",
            },
            status_code=400,
        )

    try:
        user = AuthService.create_user(db, email=email, full_name=full_name, password=password, role="patient")
        AuthService.login_user(request, user)
        return RedirectResponse(url="/dashboard", status_code=303)
    except ValueError as exc:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "user": get_current_user(request, db),
                "error": str(exc),
            },
            status_code=400,
        )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "user": get_current_user(request, db),
            "error": "",
        },
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = AuthService.authenticate_user(db, email=email, password=password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "user": get_current_user(request, db),
                "error": "Invalid email or password.",
            },
            status_code=400,
        )

    AuthService.login_user(request, user)
    next_url = "/admin" if user.role in {"doctor", "admin"} else "/dashboard"
    return RedirectResponse(url=next_url, status_code=303)


@router.get("/logout")
def logout(request: Request):
    AuthService.logout_user(request)
    return RedirectResponse(url="/", status_code=303)
