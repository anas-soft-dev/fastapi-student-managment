from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"

class AttendanceRecordSchema(BaseModel):
    student_id: int
    status: AttendanceStatus

class MarkAttendanceSchema(BaseModel):
    subject_id: int
    records: list[AttendanceRecordSchema] = Field(min_length=1)

# ---- monthly report (admin / teacher) ----

class StudentMonthlyReport(BaseModel):
    student_id: int
    student_name: str
    present: int
    absent: int
    total: int

class MonthlyReportResponse(BaseModel):
    subject_id: int
    subject_name: str
    month: int
    year: int
    report: list[StudentMonthlyReport]

# ---- student's own attendance ----

class MyAttendanceRecord(BaseModel):
    subject_id: int
    subject_name: str
    date: date
    status: str

class MyAttendanceResponse(BaseModel):
    student_id: int
    records: list[MyAttendanceRecord]
