from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_service import AIService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])
templates = Jinja2Templates(directory="app/templates")
ai_service = AIService()


class AIMessageRequest(BaseModel):
    message: str


@router.get("", response_class=HTMLResponse)
def ai_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        "ai.html",
        {
            "request": request,
            "user": user,
            "session_id": request.session.get("ai_session_id") or uuid4().hex,
        },
    )


@router.post("/message")
async def ai_message(payload: AIMessageRequest, request: Request, db: Session = Depends(get_db)):
    text = payload.message.strip()
    if not text:
        return JSONResponse({"error": "Message is required."}, status_code=400)

    session_id = request.session.get("ai_session_id")
    if not session_id:
        session_id = uuid4().hex
        request.session["ai_session_id"] = session_id

    reply = await ai_service.generate_reply(db, session_id=session_id, user_message=text)
    return {
        "reply": reply.text,
        "source": reply.source,
        "session_id": session_id,
    }
