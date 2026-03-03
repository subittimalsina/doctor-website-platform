from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Invoice, PaymentEvent


class BillingService:
    @staticmethod
    def create_invoice(
        db: Session,
        user_id: int,
        description: str,
        amount: float,
        due_days: int = 14,
    ) -> Invoice:
        invoice = Invoice(
            user_id=user_id,
            invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
            description=description.strip(),
            amount=Decimal(str(amount)),
            status="unpaid",
            due_date=datetime.utcnow() + timedelta(days=due_days),
            issued_at=datetime.utcnow(),
        )
        db.add(invoice)
        db.flush()

        event = PaymentEvent(
            invoice_id=invoice.id,
            event_type="created",
            notes="Invoice created by clinic staff.",
            created_at=datetime.utcnow(),
        )
        db.add(event)
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def mark_invoice_status(db: Session, invoice_id: int, status: str, note: str = "") -> bool:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return False
        invoice.status = status
        db.add(invoice)
        db.flush()
        db.add(
            PaymentEvent(
                invoice_id=invoice.id,
                event_type=f"status:{status}",
                notes=note,
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
        return True
