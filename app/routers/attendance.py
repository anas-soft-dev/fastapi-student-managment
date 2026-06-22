from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import extract

from app.database import get_db
from app.models.attendance import Attendance
from app.models.subject import Subject
from app.models.user import User
from app.schemas.attendance import (
    MarkAttendanceSchema,
    MonthlyReportResponse,
    StudentMonthlyReport,
    MyAttendanceResponse,
    MyAttendanceRecord,
)
from app.auth import PermissionCheck

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def ensure_subject_access(user: User, subject: Subject):
    """Admin can access any subject; a teacher only his assigned subjects."""
    if "admin" in user.role_name:
        return
    if subject not in user.taught_subjects:
        raise HTTPException(
            status_code=403,
            detail="You can only manage attendance for your assigned subjects"
        )


@router.post("")
def mark_attendance(data: MarkAttendanceSchema, db = Depends(get_db), user = Depends(PermissionCheck("mark attendance"))):
    subject = db.get(Subject, data.subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    ensure_subject_access(user, subject)

    today = date.today()
    enrolled_ids = {student.id for student in subject.students}

    marked = 0
    for record in data.records:
        if record.student_id not in enrolled_ids:
            raise HTTPException(
                status_code=422,
                detail=f"Student {record.student_id} is not enrolled in this subject"
            )

        existing = db.query(Attendance).filter(
            Attendance.student_id == record.student_id,
            Attendance.subject_id == data.subject_id,
            Attendance.date == today
        ).first()

        if existing:
            existing.status = record.status.value
        else:
            db.add(Attendance(
                student_id=record.student_id,
                subject_id=data.subject_id,
                date=today,
                status=record.status.value,
                marked_by=user.id
            ))
        marked += 1

    db.commit()

    return {
        "status": True,
        "message": f"Attendance marked for {marked} student(s)",
        "date": str(today)
    }


@router.get("/report", response_model=MonthlyReportResponse)
def monthly_report(
    subject_id: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db = Depends(get_db),
    user = Depends(PermissionCheck("view attendance report")),
):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    ensure_subject_access(user, subject)

    records = db.query(Attendance).filter(
        Attendance.subject_id == subject_id,
        extract("month", Attendance.date) == month,
        extract("year", Attendance.date) == year,
    ).all()

    summary = {}
    for record in records:
        entry = summary.setdefault(
            record.student_id,
            {"name": record.student.name, "present": 0, "absent": 0}
        )
        if record.status == "present":
            entry["present"] += 1
        else:
            entry["absent"] += 1

    report = [
        StudentMonthlyReport(
            student_id=student_id,
            student_name=entry["name"],
            present=entry["present"],
            absent=entry["absent"],
            total=entry["present"] + entry["absent"],
        )
        for student_id, entry in summary.items()
    ]

    return MonthlyReportResponse(
        subject_id=subject_id,
        subject_name=subject.name,
        month=month,
        year=year,
        report=report,
    )


@router.get("/my", response_model=MyAttendanceResponse)
def my_attendance(
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    db = Depends(get_db),
    user = Depends(PermissionCheck("view own attendance")),
):
    query = db.query(Attendance).filter(Attendance.student_id == user.id)

    if month:
        query = query.filter(extract("month", Attendance.date) == month)
    if year:
        query = query.filter(extract("year", Attendance.date) == year)

    records = query.all()

    return MyAttendanceResponse(
        student_id=user.id,
        records=[
            MyAttendanceRecord(
                subject_id=record.subject_id,
                subject_name=record.subject.name,
                date=record.date,
                status=record.status,
            )
            for record in records
        ],
    )
