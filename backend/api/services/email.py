import base64
import logging
import requests
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


def _fmt(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def send_timesheet_email(
    recipient_email: str,
    user_name: str,
    period_start: str,
    period_end: str,
    excel_bytes: bytes,
) -> None:
    if not settings.resend_api_key:
        raise ValueError("RESEND_API_KEY is not configured")

    period_str = f"{_fmt(period_start)} – {_fmt(period_end)}"
    subject = f"Timesheet — {user_name} — {period_str}"
    body = (
        f"Hi,\n\nPlease find attached the timesheet for {user_name} "
        f"covering {period_str}.\n\nThis was sent automatically by ShiftMate.\n"
    )

    filename = f"timesheet_{period_start}_{period_end}.xlsx"
    encoded = base64.b64encode(excel_bytes).decode()

    logger.info("Sending timesheet email to %s for period %s – %s", recipient_email, period_start, period_end)

    resp = requests.post(
        RESEND_URL,
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={
            "from": "ShiftMate <onboarding@resend.dev>",
            "to": [recipient_email],
            "subject": subject,
            "text": body,
            "attachments": [{"filename": filename, "content": encoded}],
        },
        timeout=15,
    )

    logger.info("Resend response: status=%s body=%s", resp.status_code, resp.text)

    if not resp.ok:
        raise RuntimeError(f"Resend error {resp.status_code}: {resp.text}")
