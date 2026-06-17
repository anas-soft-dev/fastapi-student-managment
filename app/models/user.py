from app.database import Base
from sqlalchemy import String, Text, Column, Enum as sqlEnum
from sqlalchemy.orm import Mapped, MappedColumn

from enum import Enum

class UserRole(str,Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = MappedColumn(
        primary_key = True
    )

    name: Mapped[str] = MappedColumn(String(50),nullable=True)

    email: Mapped[str] = MappedColumn(String(50), unique=True)
                                      
    password: Mapped[str] = MappedColumn(Text)

    role: Mapped[UserRole] = MappedColumn(
        sqlEnum(UserRole)
    )
    