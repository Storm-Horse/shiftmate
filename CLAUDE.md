# CLAUDE.md — ShiftMate

Tool for shift workers to log hours and automate timesheet submission.

## What this app is

ShiftMate removes the end-of-week scramble for shift workers. Users enter their hours as they work (or at the end of each shift), and the app handles building and sending the timesheet automatically on schedule — so nothing gets forgotten and payroll is never late.

Core workflow:
1. Worker clocks in / logs a shift (start time, end time, break, job code if applicable)
2. App accumulates hours across the pay period
3. At the configured cut-off, the completed timesheet is automatically sent (email, PDF, or integration with payroll system)

## What this app is NOT

- Not a rostering or scheduling tool (that's the employer's problem)
- Not a payroll processor — just the timesheet generation and delivery layer

## Stack

- **Backend:** Python 3.12 + FastAPI + SQLite (SQLAlchemy 2, no Docker needed)
- **Frontend:** React 18 + Vite + Tailwind CSS (mobile-first PWA)
- **Email:** SendGrid API
- **Spreadsheet:** openpyxl (.xlsx)

## Project structure

```
shiftmate/
  backend/      ← API + timesheet generation + scheduled sends
  mobile/       ← Primary interface (shift workers are on their phone)
  web/          ← Optional employer/admin view
  design/       ← Wireframes, design tokens, notes
```

## Key design constraints

- Workers use this on a phone, often at the start/end of a physical shift — interactions must be extremely fast (< 3 taps to log a shift)
- Timesheet format will vary by employer — output must be configurable (PDF, CSV, email body)
- Automated send is the core value prop — if the send fails silently, the app has failed
- Must handle common edge cases: overnight shifts, split shifts, public holidays, missed clock-outs

## Running locally

**Prerequisites:** Python 3.12+, Node.js 18+

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env    # fill in SENDGRID_API_KEY and SENDGRID_FROM_EMAIL
uvicorn api.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev              # http://localhost:5173
```

API docs: http://localhost:8000/api/docs

## Notes

- Launch Claude Code from within `/home/jessse/shiftmate/` to keep context isolated from other projects
