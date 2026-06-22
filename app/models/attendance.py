from datetime import date as date_type

from app.database import Base
from sqlalchemy import String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade")
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="cascade")
    )

    date: Mapped[date_type] = mapped_column(Date)

    status: Mapped[str] = mapped_column(String(20))

    marked_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    student: Mapped["User"] = relationship(
        foreign_keys=[student_id],
        lazy="selectin"
    )

    subject: Mapped["Subject"] = relationship(
        lazy="selectin"
    )

    # one attendance record per student per subject per day
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "date", name="uq_student_subject_date"),
    )
