from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Appointment, ContactLead, Invoice, SupportTicket, User


class AnalyticsService:
    @staticmethod
    def global_metrics(db: Session) -> dict:
        now = datetime.utcnow()
        seven_days = now - timedelta(days=7)

        return {
            "users_total": db.query(User).count(),
            "patients_total": db.query(User).filter(User.role == "patient").count(),
            "appointments_total": db.query(Appointment).count(),
            "appointments_week": db.query(Appointment).filter(Appointment.created_at >= seven_days).count(),
            "tickets_total": db.query(SupportTicket).count(),
            "tickets_week": db.query(SupportTicket).filter(SupportTicket.created_at >= seven_days).count(),
            "invoices_total": db.query(Invoice).count(),
            "leads_total": db.query(ContactLead).count(),
            "generated_at": now.isoformat(),
        }

    @staticmethod
    def status_breakdown(db: Session) -> dict:
        appointment_rows = db.query(Appointment.status).all()
        ticket_rows = db.query(SupportTicket.status).all()
        invoice_rows = db.query(Invoice.status).all()

        def build(items):
            out = {}
            for (value,) in items:
                out[value] = out.get(value, 0) + 1
            return out

        return {
            "appointments": build(appointment_rows),
            "tickets": build(ticket_rows),
            "invoices": build(invoice_rows),
        }
