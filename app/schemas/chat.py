from pydantic import BaseModel, Field, field_validator,EmailStr
from app.auth import make_hash
from typing import Optional


class ChatInput(BaseModel):
    message: str
    conversation_id: str


class ChatOutput(BaseModel):
    reply: str
    conversation_id: str


class AddUserInput(BaseModel):
    name: str = Field(description="The user's full name")
    email: str = Field(description="The user's email address")
    password: str = Field(description="The user's password")

    @field_validator("password")
    def hash_password(cls, value) -> str:
        return make_hash(value)

class DeleteUser(BaseModel):
    email:Optional[EmailStr]=Field(default=None,description="The user's email address")
    user_id:Optional[str]=Field(default=None, description="ID of user")
    
class UpdateUser(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Current email to find the user")
    user_id: Optional[str] = Field(None, description="Current ID to find the user")
    name: Optional[str] = Field(None, description="New name to update")
    new_email: Optional[EmailStr] = Field(None, description="New email to update")
    password: Optional[str] = Field(None, description="New password to update")
    @field_validator("password")
    def hash_password(cls, value) -> str:
        return make_hash(value)