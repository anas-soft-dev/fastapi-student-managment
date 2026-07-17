from langchain.tools import tool
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserRegisterSchema
from sqlalchemy import or_


def make_student_tools(db):

    def _student_query():
        return db.query(User).join(User.roles).filter(Role.name == "student")

    def _format_student(user: User) -> str:
        return f"id= {user.id}, name= {user.name}, email= {user.email}"

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

    @tool
    def add_student(data: UserRegisterSchema) -> str:
        existing_user = _student_query.where(User.email == data.email).first()
        if existing_user:
            return f"{data.email} already exist"
        user = User(**data.model_dump())
        role = db.query(Role).where(Role.name == "student").first()
        user.assign_role(role)

        db.add(user)
        db.commit()
        db.refresh(user)
        return f"{user}"

    return [list_students, search_student, add_student]
