from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import (
    admin,
    ai,
    announcements,
    api,
    appointments,
    auth,
    billing,
    dashboard,
    knowledge,
    notifications,
    operations,
    public,
    refills,
    records,
    support,
)

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(public.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(appointments.router)
app.include_router(support.router)
app.include_router(billing.router)
app.include_router(notifications.router)
app.include_router(records.router)
app.include_router(refills.router)
app.include_router(admin.router)
app.include_router(operations.router)
app.include_router(knowledge.router)
app.include_router(announcements.router)
app.include_router(ai.router)
app.include_router(api.router)
