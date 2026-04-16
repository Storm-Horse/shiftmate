import logging
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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
    if not settings.gmail_user or not settings.gmail_app_password:
        raise ValueError("GMAIL_USER and GMAIL_APP_PASSWORD are not configured")

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

    logger.info("Sending timesheet email to %s for period %s – %s", recipient_email, period_start, period_end)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(settings.gmail_user, settings.gmail_app_password)
        server.sendmail(settings.gmail_user, recipient_email, msg.as_string())

    logger.info("Email sent successfully to %s", recipient_email)
