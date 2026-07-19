from langchain.tools import tool
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserRegisterSchema
from app.schemas.chat import AddUserInput, DeleteUser, UpdateUser
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import or_


def make_teacher_tools(db):
    def _teacher_query():
        return db.query(User).join(User.roles).filter(Role.name == "teacher")

    def _format_teacher(user: User) -> str:
        return f"id= {user.id}, name= {user.name}, email= {user.email}"

    def _find_user(email, user_id) -> dict:
        user = (
            db.query(User).filter(or_(User.email == email, User.id == user_id)).first()
        )
        return user

    @tool
    def list_teachers() -> str:
        """list all teachers with their id, name and email"""
        users = _teacher_query().all()
        return "\n".join(_format_teacher(user) for user in users)

    @tool
    def search_teacher(query: str) -> str:
        """
        Find teachers whose name or email contains the given text.
        """
        users = (
            _teacher_query()
            .filter(or_(User.name.contains(query), User.email.contains(query)))
            .all()
        )

        return "\n".join(_format_teacher(user) for user in users)

    @tool(args_schema=AddUserInput)
    def add_teacher(name: str, email: str, password: str) -> str:
        """
        To add teacher in database use this tool
        """
        existing_user = db.query(User).where(User.email == email).first()
        if existing_user:
            return f"{email} already exist"
        user = User(name=name, email=email, password=password)
        role = db.query(Role).where(Role.name == "teacher").first()
        user.assign_role(role)

        db.add(user)
        db.commit()
        db.refresh(user)
        output = f"{user.name} is successfully added"
        return output

    @tool(args_schema=DeleteUser)
    def delete_teacher(
        email: Optional[EmailStr] = None, user_id: Optional[str] = None
    ) -> str:
        """
        Delete teacher whose email or id matches the given value.
        Provide either email or user_id.
        """

        existing_teacher = _find_user(email=email, user_id=user_id)
        if not existing_teacher:
            return "No teacher exist"
        db.delete(existing_teacher)
        db.commit()
        output = f"{existing_teacher.email} is successfully delete"
        return output

    @tool(args_schema=UpdateUser)
    def update_teacher(
        email: Optional[EmailStr] = None,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        new_email: Optional[EmailStr] = None,
        password: Optional[str] = None,
    ):
        """Update a teacher's information. Provide email or teacher_id to find the teacher, plus fields to update."""
        existing_teacher = _find_user(email=email, user_id=user_id)
        if not existing_teacher:
            return "No teacher exist"

        if name:
            existing_teacher.name = name
        if new_email:
            existing_teacher.email = new_email
        if password:
            existing_teacher.password = password

        db.commit()
        db.refresh(existing_teacher)
        output = f"{existing_teacher.email} is successfully update"
        return output

    return [list_teachers, search_teacher, add_teacher, delete_teacher, update_teacher]
