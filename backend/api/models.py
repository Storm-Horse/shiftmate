from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    recipient_email = Column(String, nullable=True)
    employer = Column(String, nullable=True)

    # Pay period config
    # type: "weekly" | "fortnightly" | "monthly"
    pay_period_type = Column(String, default="weekly")
    # weekly: 0=Mon … 6=Sun  |  monthly: 1–28 (day of month)
    pay_period_value = Column(Integer, default=0)
    # fortnightly only: ISO date string of a known period start
    pay_period_anchor = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    shifts = relationship("Shift", back_populates="user", cascade="all, delete-orphan")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date = Column(String, nullable=False)       # YYYY-MM-DD
    start_time = Column(String, nullable=True)  # HH:MM — null when direct_hours used
    end_time = Column(String, nullable=True)    # HH:MM — null when direct_hours used
    direct_hours = Column(Float, nullable=True) # set when user logs hours directly
    break_minutes = Column(Integer, default=0)
    job_name = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="shifts")
