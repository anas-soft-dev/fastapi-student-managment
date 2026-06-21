from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from enum import Enum
from app.models.role import Role
from app.auth import make_hash

class UserRole(str,Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"

class UserRegisterSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50,examples=["user"])
    email: EmailStr = Field(max_length=50,examples=["user@gmail.com"])
    password: str = Field(min_length=8,examples=["12345678"])
    @field_validator("password")
    @classmethod
    def hash_password(cls, value):
        return make_hash(value)
        

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(max_length=50,examples=["user@gmail.com"])
    password: str = Field(min_length=8,examples=["12345678"])

class PermissionResponse(BaseModel):
    id: int
    name: str

class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: list[PermissionResponse]

class UserResponse(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=50,examples=["user"])
    email: EmailStr = Field(max_length=50,examples=["user@gmail.com"])
    roles: list[RoleResponse]

class AllUserResponse(BaseModel):
    users:list[UserResponse]

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

