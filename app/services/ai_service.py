from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AIMessage


@dataclass
class AIReply:
    text: str
    source: str


class AIService:
    def __init__(self):
        self.settings = get_settings()

    def save_message(self, db: Session, session_id: str, role: str, content: str, user_id: int | None = None) -> AIMessage:
        message = AIMessage(
            session_id=session_id,
            role=role,
            content=content,
            user_id=user_id,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_recent_context(self, db: Session, session_id: str, limit: int = 10) -> list[AIMessage]:
        return (
            db.query(AIMessage)
            .filter(AIMessage.session_id == session_id)
            .order_by(AIMessage.created_at.desc())
            .limit(limit)
            .all()[::-1]
        )

    async def generate_reply(self, db: Session, session_id: str, user_message: str) -> AIReply:
        self.save_message(db, session_id=session_id, role="user", content=user_message)

        if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
            ai_text = await self._call_openai(db, session_id)
            source = "openai"
        else:
            ai_text = self._mock_reply(user_message)
            source = "mock"

        self.save_message(db, session_id=session_id, role="assistant", content=ai_text)
        return AIReply(text=ai_text, source=source)

    async def _call_openai(self, db: Session, session_id: str) -> str:
        context = self.get_recent_context(db, session_id)
        system_prompt = (
            "You are a clinical website assistant for a doctor office. "
            "You can provide general guidance, appointment info, and support instructions. "
            "Do not give medical diagnosis. If user asks urgent medical help, ask them to call emergency services."
        )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in context:
            messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.settings.openai_model,
            "messages": messages,
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return self._mock_reply(context[-1].content if context else "")

    def _mock_reply(self, user_message: str) -> str:
        text = user_message.lower().strip()
        if "appointment" in text:
            return "I can help with appointments. Please open the appointment page, choose a date/time, and submit your request."
        if "urgent" in text or "emergency" in text:
            return "For urgent symptoms, contact your local emergency number immediately. This chat is not emergency care."
        if "support" in text or "ticket" in text:
            return "You can create a support ticket from the Support page. Our staff will reply from the dashboard."
        if "hello" in text or "hi" in text:
            return "Hello. I can guide you through appointments, support requests, and clinic information."
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        return (
            "I can provide general clinic guidance and website help. "
            "For medical decisions, please consult the doctor directly. "
            f"(assistant generated at {now})"
        )
