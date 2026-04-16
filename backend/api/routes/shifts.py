from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user
from ..services.timesheet import compute_hours

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _to_out(shift: models.Shift) -> schemas.ShiftOut:
    return schemas.ShiftOut(
        id=shift.id,
        date=shift.date,
        start_time=shift.start_time,
        end_time=shift.end_time,
        direct_hours=shift.direct_hours,
        break_minutes=shift.break_minutes,
        job_name=shift.job_name,
        notes=shift.notes,
        hours=compute_hours(shift.start_time, shift.end_time, shift.break_minutes, shift.direct_hours),
    )


@router.post("", response_model=schemas.ShiftOut, status_code=201)
def create_shift(
    data: schemas.ShiftCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    shift = models.Shift(user_id=current_user.id, **data.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return _to_out(shift)


@router.get("", response_model=List[schemas.ShiftOut])
def list_shifts(
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Shift).filter(models.Shift.user_id == current_user.id)
    if start:
        q = q.filter(models.Shift.date >= start)
    if end:
        q = q.filter(models.Shift.date <= end)
    return [_to_out(s) for s in q.order_by(models.Shift.date, models.Shift.start_time).all()]


@router.get("/jobs", response_model=List[str])
def list_job_names(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Distinct job names for autocomplete."""
    rows = (
        db.query(models.Shift.job_name)
        .filter(models.Shift.user_id == current_user.id)
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


@router.delete("/{shift_id}", status_code=204)
def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    shift = (
        db.query(models.Shift)
        .filter(models.Shift.id == shift_id, models.Shift.user_id == current_user.id)
        .first()
    )
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    db.delete(shift)
    db.commit()
