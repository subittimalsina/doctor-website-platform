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

        source = "mock"
        ai_text = self._mock_reply(user_message)
        provider = (self.settings.ai_provider or "mock").strip().lower()

        if provider == "openai":
            if self.settings.openai_api_key:
                ai_text = await self._call_openai(db, session_id)
                source = "openai"
        elif provider == "openai_compatible":
            ai_text = await self._call_openai_compatible(
                db,
                session_id=session_id,
                base_url=self.settings.local_ai_base_url,
                model=self.settings.local_ai_model,
                api_key=self.settings.local_ai_api_key,
            )
            source = "openai_compatible"
        elif provider == "ollama":
            ai_text = await self._call_ollama(db, session_id=session_id)
            source = "ollama"

        self.save_message(db, session_id=session_id, role="assistant", content=ai_text)
        return AIReply(text=ai_text, source=source)

    async def _call_openai(self, db: Session, session_id: str) -> str:
        return await self._call_openai_compatible(
            db,
            session_id=session_id,
            base_url=self.settings.openai_base_url,
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
        )

    async def _call_openai_compatible(
        self,
        db: Session,
        session_id: str,
        base_url: str,
        model: str,
        api_key: str,
    ) -> str:
        context = self.get_recent_context(db, session_id)
        messages = self._build_messages(context)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.4,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint = self._resolve_openai_chat_url(base_url)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return self._mock_reply(context[-1].content if context else "")

    async def _call_ollama(self, db: Session, session_id: str) -> str:
        context = self.get_recent_context(db, session_id)
        messages = self._build_messages(context)
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": False,
        }
        endpoint = self.settings.ollama_base_url.rstrip("/") + "/api/chat"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(endpoint, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "").strip()
                if content:
                    return content
                return self._mock_reply(context[-1].content if context else "")
        except Exception:
            return self._mock_reply(context[-1].content if context else "")

    def _build_messages(self, context: list[AIMessage]) -> list[dict]:
        system_prompt = (
            "You are a clinical website assistant for a doctor office. "
            "You can provide general guidance, appointment info, and support instructions. "
            "Do not give medical diagnosis. If user asks urgent medical help, ask them to call emergency services."
        )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in context:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    def _resolve_openai_chat_url(self, base_url: str) -> str:
        base = (base_url or "").strip().rstrip("/")
        if not base:
            base = "https://api.openai.com/v1"
        if base.endswith("/chat/completions"):
            return base
        if base.endswith("/v1"):
            return base + "/chat/completions"
        return base + "/v1/chat/completions"

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
