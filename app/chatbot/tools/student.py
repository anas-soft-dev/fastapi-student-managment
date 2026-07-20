from langchain.tools import tool
from app.models.user import User
from app.models.role import Role
from sqlalchemy import or_
from app.auth import make_hash


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
    
    @tool
    def add_student(name: str, email: str, password: str)->str:
        """
            Add a new student with the given name, email, and password.
            Arguments:
            - name: The name of the student.
            - email: The email of the student.
            - password: The password of the student.
        """

        hash_password = make_hash(password)
        new_student = User(name=name, email=email, password=hash_password)
        student_role = db.query(Role).filter(Role.name == "student").first()
        if not student_role:
            return "Student role not found."
        
        new_student.roles.append(student_role)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return f"Added student: {_format_student(new_student)}"
    
    @tool
    def remove_student(email_or_id: str)->str:
        """
            Remove a student by their email or ID.
            Arguments:
            - email_or_id: The email or ID of the student to be removed.
        """
        student = _student_query().filter(
            or_(
                User.id == email_or_id,
                User.email == email_or_id
            )
        ).first()
        if not student:
            return f"No student found with email or ID {email_or_id}."
        
        db.delete(student)
        db.commit()
        return f"Removed student: {_format_student(student)}"
    
    @tool
    def update_student(email_or_id: str, name: str = None, password: str = None)->str:
        """
            Update a student's information by their email or ID.
            Arguments:
            - email_or_id: The email or ID of the student to be updated.
            - name: The new name of the student (optional).
            - password: The new password of the student (optional).
        """

        student = _student_query().filter(
            or_(
                User.id == email_or_id,
                User.email == email_or_id
            )
        ).first()
        if not student:
            return f"No student found with email or ID {email_or_id}."
        
        if name:
            student.name = name
        if password:
            student.password = make_hash(password)
        
        db.commit()
        db.refresh(student)
        return f"Updated student: {_format_student(student)}"

    return [list_students, search_student, add_student, remove_student, update_student]