from app.database import Base
from sqlalchemy import String, Text, Column, Enum as sqlEnum
from sqlalchemy.orm import Mapped, MappedColumn, relationship
from app.database import get_db
from fastapi import Depends, HTTPException
from app.models.role import Role

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

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin"
    )

    subjects: Mapped[list["Subject"]] = relationship(
        secondary="student_subjects",
        back_populates="students",
        lazy="selectin"
    )

    taught_subjects: Mapped[list["Subject"]] = relationship(
        secondary="teacher_subjects",
        back_populates="teachers",
        lazy="selectin"
    )

    @property
    def permissions(self):
        return {
                    permission.name
                    for role in self.roles 
                    for permission in role.permissions
                }
    @property
    def role_name(self):
        return {
                    role.name
                    for role in self.roles
                }
    
    def assign_role(self, role: Role):
        if not role:
            raise HTTPException(
                status_code=404,
                detail="role does not exists"
            )
        
        self.roles.append(role)
    