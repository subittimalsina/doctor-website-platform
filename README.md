# Doctor Website Platform (Python Backend + AI + Support)

A full-stack doctor website system with:
- Python backend (`FastAPI`)
- Public clinic website pages
- User authentication (patient + doctor/admin roles)
- Appointment booking and management
- Support ticket system with threaded replies
- CMS for website pages
- Asset and website file uploads
- Blog and FAQ knowledge center
- Billing/invoice management
- In-app user notifications
- Time-bound announcement publishing
- Medication refill request workflow
- Contact inquiry intake and admin leads board
- Analytics and audit reporting
- AI assistant endpoint and chat UI

## Stack
- Backend: FastAPI + SQLAlchemy + Session middleware
- Database: SQLite (default)
- Frontend: Jinja templates + custom CSS + JavaScript
- AI: OpenAI-compatible chat completion mode (optional), with fallback mock mode

## Project Structure

```text
app/
  config.py
  database.py
  main.py
  models/
  routers/
  schemas/
  services/
  templates/
  static/
scripts/
tests/
requirements.txt
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
python scripts/seed_data.py
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000`

## Seeded Logins
- Doctor: `doctor@clinic.local` / `Doctor@123`
- Admin: `admin@clinic.local` / `Admin@123`
- Patient: `patient@clinic.local` / `Patient@123`

## AI Setup
By default, AI runs in mock mode (`AI_PROVIDER=mock`).

Supported providers:
- `mock`
- `openai`
- `openai_compatible` (LM Studio, vLLM, LocalAI, etc.)
- `ollama`

OpenAI:
1. Set `AI_PROVIDER=openai`
2. Set `OPENAI_API_KEY`
3. Optionally set `OPENAI_MODEL` and `OPENAI_BASE_URL`

OpenAI-compatible local server:
1. Start your local server (example LM Studio/vLLM) on a URL like `http://127.0.0.1:1234/v1`
2. Set:
   - `AI_PROVIDER=openai_compatible`
   - `LOCAL_AI_BASE_URL=http://127.0.0.1:1234/v1`
   - `LOCAL_AI_MODEL=<your-local-model-name>`
   - `LOCAL_AI_API_KEY=<optional>`

Ollama:
1. Start Ollama and pull a model (example):
   - `ollama pull llama3.1:8b`
   - `ollama serve`
2. Set:
   - `AI_PROVIDER=ollama`
   - `OLLAMA_BASE_URL=http://127.0.0.1:11434`
   - `OLLAMA_MODEL=llama3.1:8b`

## Main Routes
- Public: `/`, `/about`, `/services`, `/contact`, `/page/{slug}`
- Auth: `/auth/register`, `/auth/login`, `/auth/logout`
- Dashboard: `/dashboard`
- Appointments: `/appointments/book`, `/appointments/my`, `/appointments/manage`
- Support: `/support/new`, `/support/my`, `/support/{ticket_id}`, `/support/manage/all`
- Announcements: `/announcements`, `/admin/announcements`
- Refills: `/refills/new`, `/refills/my`, `/refills/{refill_id}`, `/refills/manage/all`
- Records: `/records/my`, `/records/{record_id}`, `/records/manage`
- Billing: `/billing/my`, `/billing/manage`
- Notifications: `/notifications`
- Admin: `/admin`, `/admin/pages`, `/admin/uploads`
- Admin Ops: `/admin/blog`, `/admin/faq`, `/admin/leads`, `/admin/reports`
- Knowledge: `/blog`, `/blog/{slug}`, `/faq`
- AI: `/ai`, `/ai/message`
- API: `/api/health`, `/api/pages`, `/api/stats`, `/api/knowledge`, `/api/reports/metrics`, `/api/reports/status`, `/api/counts/public`, `/api/records/my`, `/api/announcements`, `/api/refills/my`

## Tests

```bash
pytest -q
```

## Production Notes
- Replace `SECRET_KEY`.
- Use PostgreSQL/MySQL instead of SQLite.
- Configure reverse proxy and TLS.
- Add role provisioning workflows, password reset, and audit logs.
- Add email/SMS notifications for appointment and ticket updates.
- Add healthcare compliance controls suited to your legal jurisdiction.
