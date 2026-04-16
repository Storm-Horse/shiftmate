import base64
import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition,
)
from ..config import settings

logger = logging.getLogger(__name__)


def _fmt(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def send_timesheet_email(
    recipient_email: str,
    user_name: str,
    period_start: str,
    period_end: str,
    excel_bytes: bytes,
) -> None:
    if not settings.sendgrid_api_key:
        raise ValueError("SENDGRID_API_KEY is not configured")

    period_str = f"{_fmt(period_start)} – {_fmt(period_end)}"
    subject = f"Timesheet — {user_name} — {period_str}"

    body = (
        f"Hi,\n\n"
        f"Please find attached the timesheet for {user_name} "
        f"covering {period_str}.\n\n"
        f"This was sent automatically by ShiftMate.\n"
    )

    message = Mail(
        from_email=(settings.sendgrid_from_email, settings.sendgrid_from_name),
        to_emails=recipient_email,
        subject=subject,
        plain_text_content=body,
    )

    encoded = base64.b64encode(excel_bytes).decode()
    attachment = Attachment(
        FileContent(encoded),
        FileName(f"timesheet_{period_start}_{period_end}.xlsx"),
        FileType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        Disposition("attachment"),
    )
    message.attachment = attachment

    logger.info("Sending timesheet email to %s for period %s – %s", recipient_email, period_start, period_end)

    client = SendGridAPIClient(settings.sendgrid_api_key)
    response = client.send(message)

    logger.info(
        "SendGrid response: status=%s headers=%s body=%s",
        response.status_code,
        dict(response.headers),
        response.body,
    )

    if response.status_code not in (200, 201, 202):
        raise RuntimeError(f"SendGrid error {response.status_code}: {response.body}")
