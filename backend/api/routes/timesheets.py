from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user
from ..services.timesheet import generate_excel
from ..services.email import send_timesheet_email

router = APIRouter(prefix="/timesheets", tags=["timesheets"])


def _get_shifts(db, user_id, period_start, period_end):
    return (
        db.query(models.Shift)
        .filter(
            models.Shift.user_id == user_id,
            models.Shift.date >= period_start,
            models.Shift.date <= period_end,
        )
        .order_by(models.Shift.date, models.Shift.start_time)
        .all()
    )


@router.post("/send")
def send_timesheet(
    data: schemas.SendTimesheetRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    shifts = _get_shifts(db, current_user.id, data.period_start, data.period_end)
    if not shifts:
        raise HTTPException(status_code=400, detail="No shifts found in this period")

    recipient = data.recipient_email or current_user.recipient_email
    if not recipient:
        raise HTTPException(status_code=400, detail="No recipient email configured")

    excel_bytes = generate_excel(current_user, shifts, data.period_start, data.period_end)
    send_timesheet_email(recipient, current_user.name, data.period_start, data.period_end, excel_bytes)

    return {"message": f"Timesheet sent to {recipient}"}


@router.get("/download")
def download_timesheet(
    period_start: str,
    period_end: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    shifts = _get_shifts(db, current_user.id, period_start, period_end)
    if not shifts:
        raise HTTPException(status_code=400, detail="No shifts found in this period")

    excel_bytes = generate_excel(current_user, shifts, period_start, period_end)
    filename = f"timesheet_{period_start}_{period_end}.xlsx"

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
