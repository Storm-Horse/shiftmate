import base64
import logging
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from ..config import settings

logger = logging.getLogger(__name__)

GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def _get_access_token() -> str:
    resp = requests.post(GMAIL_TOKEN_URL, data={
        "grant_type": "refresh_token",
        "client_id": settings.gmail_client_id,
        "client_secret": settings.gmail_client_secret,
        "refresh_token": settings.gmail_refresh_token,
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def _fmt(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def send_timesheet_email(
    recipient_email: str,
    user_name: str,
    period_start: str,
    period_end: str,
    excel_bytes: bytes,
) -> None:
    if not settings.gmail_client_id:
        raise ValueError("Gmail OAuth credentials are not configured")

    period_str = f"{_fmt(period_start)} – {_fmt(period_end)}"
    subject = f"Timesheet — {user_name} — {period_str}"
    body = (
        f"Hi,\n\n"
        f"Please find attached the timesheet for {user_name} "
        f"covering {period_str}.\n\n"
        f"This was sent automatically by ShiftMate.\n"
    )

    msg = MIMEMultipart()
    msg["From"] = settings.gmail_user
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    attachment = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    attachment.set_payload(excel_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f'attachment; filename="timesheet_{period_start}_{period_end}.xlsx"',
    )
    msg.attach(attachment)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    logger.info("Sending timesheet email to %s for period %s – %s", recipient_email, period_start, period_end)

    access_token = _get_access_token()
    resp = requests.post(
        GMAIL_SEND_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json={"raw": raw},
        timeout=15,
    )

    logger.info("Gmail API response: status=%s body=%s", resp.status_code, resp.text)

    if not resp.ok:
        raise RuntimeError(f"Gmail API error {resp.status_code}: {resp.text}")
