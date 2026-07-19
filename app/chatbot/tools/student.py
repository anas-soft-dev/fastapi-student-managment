from langchain.tools import tool
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserRegisterSchema
from app.schemas.chat import AddUserInput, DeleteUser, UpdateUser
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import or_


def make_student_tools(db):

    def _student_query():
        return db.query(User).join(User.roles).filter(Role.name == "student")

    def _format_student(user: User) -> str:
        return f"id= {user.id}, name= {user.name}, email= {user.email}"

    def _find_user(email, student_id) -> dict:
        user = (
            db.query(User)
            .filter(or_(User.email == email, User.id == student_id))
            .first()
        )
        return user

    @tool
    def list_students() -> str:
        """list all students with their id, name and email"""
        users = _student_query().all()
        return "\n".join(_format_student(user) for user in users)

    @tool
    def search_student(query: str) -> str:
        """
        Find students whose name or email contains the given text.
        """
        users = (
            _student_query()
            .filter(or_(User.name.contains(query), User.email.contains(query)))
            .all()
        )

        return "\n".join(_format_student(user) for user in users)

    @tool(args_schema=AddUserInput)
    def add_student(name: str, email: str, password: str) -> str:
        """
        To add student in database use this tool
        """
        existing_user = db.query(User).where(User.email == email).first()
        if existing_user:
            return f"{email} already exist"
        user = User(name=name, email=email, password=password)
        role = db.query(Role).where(Role.name == "student").first()
        user.assign_role(role)

        db.add(user)
        db.commit()
        db.refresh(user)
        output = f"{user.name} is successfully added"
        return output

    @tool(args_schema=DeleteUser)
    def delete_student(
        email: Optional[EmailStr] = None, student_id: Optional[str] = None
    ) -> str:
        """
        Delete student whose email or id matches the given value.
        Provide either email or student_id.
        """

        existing_student = _find_user()
        if not existing_student:
            return "No student exist"
        db.delete(existing_student)
        db.commit()
        output = f"{existing_student.email} is successfully delete"
        return output

    @tool(args_schema=UpdateUser)
    def update_student(
        email: Optional[EmailStr] = None,
        student_id: Optional[str] = None,
        name: Optional[str] = None,
        new_email: Optional[EmailStr] = None,
        password: Optional[str] = None,
    ):
        """Update a student's information. Provide email or student_id to find the student, plus fields to update."""
        existing_student = _find_user(email=email, student_id=student_id)
        if not existing_student:
            return "No student exist"

        if name:
            existing_student.name = name
        if new_email:
            existing_student.email = new_email
        if password:
            existing_student.password = password

        db.commit()
        db.refresh(existing_student)
        output = f"{existing_student.email} is successfully update"
        return output

    return [list_students, search_student, add_student, delete_student, update_student]
