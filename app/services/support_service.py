from datetime import datetime

from sqlalchemy.orm import Session

from app.models import SupportMessage, SupportTicket


class SupportService:
    @staticmethod
    def create_ticket(
        db: Session,
        user_id: int,
        subject: str,
        category: str,
        priority: str,
        message: str,
    ) -> SupportTicket:
        ticket = SupportTicket(
            user_id=user_id,
            subject=subject.strip(),
            category=category,
            priority=priority,
            status="open",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(ticket)
        db.flush()

        first_message = SupportMessage(
            ticket_id=ticket.id,
            sender_role="patient",
            message=message.strip(),
            created_at=datetime.utcnow(),
        )
        db.add(first_message)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def add_message(db: Session, ticket_id: int, sender_role: str, message: str) -> SupportMessage:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError("Ticket not found")

        msg = SupportMessage(
            ticket_id=ticket_id,
            sender_role=sender_role,
            message=message.strip(),
            created_at=datetime.utcnow(),
        )
        ticket.updated_at = datetime.utcnow()
        if sender_role in {"doctor", "admin"} and ticket.status == "resolved":
            ticket.status = "open"

        db.add(msg)
        db.add(ticket)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def change_status(db: Session, ticket_id: int, status: str) -> bool:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return False
        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        db.add(ticket)
        db.commit()
        return True
