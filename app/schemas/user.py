from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class UserRole(str,Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"

class UserRegisterSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50,examples=["user"])
    email: EmailStr = Field(max_length=50,examples=["user@gmail.com"])
    password: str = Field(min_length=8,examples=["12345678"])
    role: UserRole