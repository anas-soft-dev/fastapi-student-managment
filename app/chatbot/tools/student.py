from langchain.tools import tool
from app.models.user import User
from app.models.role import Role
from sqlalchemy import or_


def make_student_tools(db):

    def _student_query():
      return db.query(User).join(User.roles).filter(Role.name == "student")
    
    def _format_student(user: User)->str:
        return f"id= {user.id}, name= {user.name}, email= {user.email}"

    @tool
    def list_students()->str:
        """list all students with their id, name and email"""
        users = _student_query().all()
        return "\n".join(_format_student(user) for user in users)
    
    @tool
    def search_student(query: str)->str:
        """
            Find students whose name or email contains the given text.
        """
        users = _student_query().filter(
            or_(
                User.name.contains(query),
                User.email.contains(query)
            )
        ).all()

        return "\n".join(_format_student(user) for user in users)
    
    return [list_students, search_student]