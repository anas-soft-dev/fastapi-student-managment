from langchain.tools import tool
from app.models.user import User
from app.models.role import Role


def make_teacher_tools(db):
    def _format_teacher(user: User)->str:
        return f"id= {user.id}, name= {user.name}, email= {user.email}"

    @tool
    def list_teacher()->str:
        """list all teachers with their id, name and email"""
        users = db.query(User).join(User.roles).filter(Role.name == "teacher").all()
        return "\n".join(_format_teacher(user) for user in users)
    
    return [list_teacher]