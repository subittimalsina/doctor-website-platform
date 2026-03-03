from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.models import (
    Announcement,
    Appointment,
    AuditLog,
    BlogPost,
    CMSPage,
    ContactLead,
    FAQItem,
    Invoice,
    MedicalRecord,
    Notification,
    Prescription,
    RefillRequest,
    SupportMessage,
    SupportTicket,
    User,
)
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService


def seed_users(db):
    doctor_email = "doctor@clinic.local"
    admin_email = "admin@clinic.local"
    patient_email = "patient@clinic.local"

    doctor = AuthService.get_user_by_email(db, doctor_email)
    admin = AuthService.get_user_by_email(db, admin_email)
    patient = AuthService.get_user_by_email(db, patient_email)

    if not doctor:
        doctor = AuthService.create_user(
            db,
            email=doctor_email,
            full_name="Dr. Alex Morgan",
            password="Doctor@123",
            role="doctor",
        )
    if not admin:
        admin = AuthService.create_user(
            db,
            email=admin_email,
            full_name="Clinic Admin",
            password="Admin@123",
            role="admin",
        )
    if not patient:
        patient = AuthService.create_user(
            db,
            email=patient_email,
            full_name="Sample Patient",
            password="Patient@123",
            role="patient",
        )
    return doctor, admin, patient


def seed_pages(db):
    pages = [
        {
            "slug": "telehealth",
            "title": "Telehealth Visits",
            "summary": "How to join virtual consultation sessions.",
            "body": "<h2>Virtual Care</h2><p>Use your account dashboard to request telehealth appointments.</p>",
        },
        {
            "slug": "insurance",
            "title": "Insurance and Billing",
            "summary": "Accepted plans and claims workflow.",
            "body": "<h2>Insurance Support</h2><p>Open a support ticket for billing queries.</p>",
        },
        {
            "slug": "patient-rights",
            "title": "Patient Rights and Responsibilities",
            "summary": "Guidelines for appointments, records, and communication.",
            "body": "<h2>Patient Rights</h2><p>Patients can request records and report concerns through support tickets.</p>",
        },
    ]

    for page in pages:
        exists = db.query(CMSPage).filter(CMSPage.slug == page["slug"]).first()
        if exists:
            continue
        db.add(
            CMSPage(
                slug=page["slug"],
                title=page["title"],
                summary=page["summary"],
                body=page["body"],
                is_published="yes",
            )
        )
    db.commit()


def seed_appointments_and_tickets(db, patient):
    if db.query(Appointment).count() == 0:
        db.add(
            Appointment(
                patient_id=patient.id,
                reason="Routine blood pressure review",
                notes="Patient requested morning slot.",
                appointment_time=datetime.utcnow() + timedelta(days=3),
                status="pending",
            )
        )

    if db.query(SupportTicket).count() == 0:
        ticket = SupportTicket(
            user_id=patient.id,
            subject="Issue downloading prescription",
            category="technical",
            priority="normal",
            status="open",
        )
        db.add(ticket)
        db.flush()
        db.add(
            SupportMessage(
                ticket_id=ticket.id,
                sender_role="patient",
                message="The prescription PDF link does not open from my dashboard.",
            )
        )
    db.commit()


def seed_knowledge(db):
    blog_posts = [
        {
            "slug": "winter-health-checklist",
            "title": "Winter Health Checklist for Families",
            "excerpt": "Simple habits to stay prepared during seasonal changes.",
            "body": "<h2>Checklist</h2><ul><li>Stay hydrated</li><li>Keep vaccines updated</li><li>Schedule preventive checkups</li></ul>",
            "author": "Dr. Alex Morgan",
            "tags": "wellness,seasonal",
        },
        {
            "slug": "preparing-for-first-visit",
            "title": "Preparing for Your First Clinic Visit",
            "excerpt": "Documents and details to bring for efficient care.",
            "body": "<h2>Before you arrive</h2><p>Bring ID, prior reports, current medication list, and insurance details.</p>",
            "author": "Clinic Team",
            "tags": "new-patient,appointments",
        },
    ]

    for post in blog_posts:
        exists = db.query(BlogPost).filter(BlogPost.slug == post["slug"]).first()
        if exists:
            continue
        db.add(
            BlogPost(
                slug=post["slug"],
                title=post["title"],
                excerpt=post["excerpt"],
                body=post["body"],
                author=post["author"],
                tags=post["tags"],
                is_published="yes",
            )
        )

    faqs = [
        {
            "question": "How do I book an appointment?",
            "answer": "Sign in, open Book Appointment, choose date and submit reason.",
            "category": "appointments",
            "order_index": 1,
        },
        {
            "question": "How can I contact support?",
            "answer": "Use Support -> New Ticket and include detailed issue context.",
            "category": "support",
            "order_index": 2,
        },
        {
            "question": "Can I use AI assistant for medical diagnosis?",
            "answer": "No. The AI assistant gives website and workflow help, not diagnosis.",
            "category": "ai",
            "order_index": 3,
        },
    ]

    for item in faqs:
        exists = db.query(FAQItem).filter(FAQItem.question == item["question"]).first()
        if exists:
            continue
        db.add(
            FAQItem(
                question=item["question"],
                answer=item["answer"],
                category=item["category"],
                order_index=item["order_index"],
                is_published="yes",
            )
        )

    db.commit()


def seed_billing_notifications_and_leads(db, patient):
    if db.query(Invoice).count() == 0:
        BillingService.create_invoice(
            db,
            user_id=patient.id,
            description="General consultation and lab follow-up",
            amount=149.0,
            due_days=10,
        )

    if db.query(Notification).count() == 0:
        db.add(
            Notification(
                user_id=patient.id,
                title="Appointment Reminder",
                message="You have a pending appointment request. Please check status tomorrow.",
                kind="appointment",
                is_read=False,
            )
        )
        db.add(
            Notification(
                user_id=patient.id,
                title="Support Update",
                message="Your support ticket has been received by the clinic team.",
                kind="support",
                is_read=False,
            )
        )

    if db.query(ContactLead).count() == 0:
        db.add(
            ContactLead(
                full_name="Jordan Smith",
                email="jordan@example.com",
                phone="+1-555-303-8877",
                subject="Telehealth availability",
                message="Can I schedule a telehealth consultation for next week?",
                status="new",
            )
        )

    db.commit()


def seed_announcements(db, doctor):
    if db.query(Announcement).count() > 0:
        return

    now = datetime.utcnow()
    announcements = [
        Announcement(
            title="Weekend Telehealth Slots Open",
            content="New Saturday telehealth slots are available for follow-up consultations.",
            importance="high",
            status="published",
            publish_start=now - timedelta(days=1),
            publish_end=now + timedelta(days=30),
            created_by=doctor.email,
        ),
        Announcement(
            title="Support Desk Response Time",
            content="Support desk currently responds within 4 business hours for non-urgent requests.",
            importance="normal",
            status="published",
            publish_start=now - timedelta(days=2),
            publish_end=now + timedelta(days=20),
            created_by=doctor.email,
        ),
    ]
    for ann in announcements:
        db.add(ann)
    db.commit()


def seed_records(db, patient, doctor):
    if db.query(MedicalRecord).count() == 0:
        record = MedicalRecord(
            patient_id=patient.id,
            record_title="Hypertension Follow-up",
            diagnosis_summary="Mild hypertension under monitoring.",
            observations="BP trending stable. No acute distress.",
            recommendations="Continue low-sodium diet and daily walking.",
            status="active",
            created_by=doctor.email,
        )
        db.add(record)
        db.flush()
        db.add(
            Prescription(
                record_id=record.id,
                medicine_name="Amlodipine",
                dosage="5 mg",
                schedule="Once daily after breakfast",
                duration="30 days",
                notes="Review BP log in next visit.",
            )
        )
    db.commit()


def seed_refills(db, patient):
    if db.query(RefillRequest).count() > 0:
        return
    db.add(
        RefillRequest(
            patient_id=patient.id,
            medication_name="Amlodipine",
            dosage="5 mg once daily",
            current_supply_days=4,
            pharmacy_name="City Pharmacy",
            pharmacy_phone="+1-555-777-9090",
            notes="Need refill before weekend.",
            status="submitted",
        )
    )
    db.commit()


def seed_audit_logs(db, admin_email):
    if db.query(AuditLog).count() > 0:
        return

    actions = [
        ("system.bootstrap", "System", "0", "Initial system data seeded."),
        ("content.publish", "CMSPage", "telehealth", "Published Telehealth page."),
        ("support.ticket", "SupportTicket", "1", "Created sample support ticket."),
        ("billing.create", "Invoice", "1", "Created sample invoice for demo patient."),
    ]

    for action, target_type, target_id, notes in actions:
        db.add(
            AuditLog(
                actor_email=admin_email,
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                notes=notes,
            )
        )
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        doctor, admin, patient = seed_users(db)
        seed_pages(db)
        seed_appointments_and_tickets(db, patient)
        seed_knowledge(db)
        seed_billing_notifications_and_leads(db, patient)
        seed_announcements(db, doctor)
        seed_records(db, patient, doctor)
        seed_refills(db, patient)
        seed_audit_logs(db, admin.email)
        print("Seed complete.")
        print("Doctor login: doctor@clinic.local / Doctor@123")
        print("Admin login: admin@clinic.local / Admin@123")
        print("Patient login: patient@clinic.local / Patient@123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
