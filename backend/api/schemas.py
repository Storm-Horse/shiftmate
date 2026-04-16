from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    recipient_email: Optional[str]
    employer: Optional[str]
    pay_period_type: str
    pay_period_value: int
    pay_period_anchor: Optional[str]

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    recipient_email: Optional[str] = None
    employer: Optional[str] = None
    pay_period_type: Optional[str] = None
    pay_period_value: Optional[int] = None
    pay_period_anchor: Optional[str] = None


class ShiftCreate(BaseModel):
    date: str                       # YYYY-MM-DD
    start_time: Optional[str] = None  # HH:MM — required unless direct_hours set
    end_time: Optional[str] = None    # HH:MM — required unless direct_hours set
    direct_hours: Optional[float] = None  # use instead of start/end times
    break_minutes: int = 0
    job_name: str
    notes: Optional[str] = None

    @model_validator(mode="after")
    def check_times_or_hours(self):
        has_times = self.start_time and self.end_time
        has_hours = self.direct_hours is not None
        if not has_times and not has_hours:
            raise ValueError("Provide either start_time + end_time, or direct_hours")
        if has_times and has_hours:
            raise ValueError("Provide either start_time + end_time or direct_hours, not both")
        return self


class ShiftOut(BaseModel):
    id: int
    date: str
    start_time: Optional[str]
    end_time: Optional[str]
    direct_hours: Optional[float]
    break_minutes: int
    job_name: str
    notes: Optional[str]
    hours: float

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class SendTimesheetRequest(BaseModel):
    period_start: str           # YYYY-MM-DD
    period_end: str             # YYYY-MM-DD
    recipient_email: Optional[str] = None  # overrides user default if provided
