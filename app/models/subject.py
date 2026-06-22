from app.database import Base
from sqlalchemy import String, Text, Column, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(String(50), unique=True)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    students: Mapped[list["User"]] = relationship(
        secondary="student_subjects",
        back_populates="subjects",
        lazy="selectin"
    )

    teachers: Mapped[list["User"]] = relationship(
        secondary="teacher_subjects",
        back_populates="taught_subjects",
        lazy="selectin"
    )

student_subjects = Table(
    "student_subjects", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="cascade"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id", ondelete="cascade"), primary_key=True)
)

teacher_subjects = Table(
    "teacher_subjects", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="cascade"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id", ondelete="cascade"), primary_key=True)
)
