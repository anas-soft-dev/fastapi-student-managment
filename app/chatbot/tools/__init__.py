from app.chatbot.tools.student import make_student_tools
from app.chatbot.tools.teacher import make_teacher_tools

def get_tools(db):
    return [
        *make_student_tools(db),
        *make_teacher_tools(db)
    ]