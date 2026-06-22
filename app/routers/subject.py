from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.subject import Subject
from app.models.user import User
from app.models.role import Role
from app.schemas.subject import AllSubjectResponse, SubjectSchema, SubjectResponse
from app.schemas.user import AllUserResponse
from app.auth import PermissionCheck

router = APIRouter(prefix="/subject", tags=["Subject"])

@router.get("",response_model=AllSubjectResponse)
def view(db = Depends(get_db), user = Depends(PermissionCheck("view subject"))):
    subjects = db.query(Subject).all()
    return {"subjects":subjects}

@router.post("",response_model=SubjectResponse)
def store(data: SubjectSchema, db=Depends(get_db), user = Depends(PermissionCheck("add subject"))):
    exist_subject = db.query(Subject).where(Subject.name == data.name).first()
    if exist_subject:
        raise HTTPException(
            status_code=422,
            detail="Subject already Exists"
        )
    subject = Subject(**data.model_dump())

    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.put("/{subject_id}", response_model=SubjectResponse)
def update(subject_id: int, data: SubjectSchema, db = Depends(get_db), user = Depends(PermissionCheck("edit subject"))):
    subject = db.get(Subject, subject_id)

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    subject.name = data.name
    subject.description = data.description

    db.commit()
    db.refresh(subject)

    return subject

@router.delete("/{subject_id}")
def delete(subject_id:int, db= Depends(get_db), user = Depends(PermissionCheck("delete subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    db.delete(subject)
    db.commit()

    return {
        "status":True,
        "message": "Successfully deleted"
    }

@router.post("/{subject_id}/student/{student_id}")
def assign_subject(subject_id: int, student_id: int, db = Depends(get_db), user = Depends(PermissionCheck("assign subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    student = db.get(User, student_id)
    if not student or "student" not in student.role_name:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    if subject in student.subjects:
        raise HTTPException(
            status_code=422,
            detail="Subject already assigned to this student"
        )

    student.subjects.append(subject)
    db.commit()

    return {
        "status":True,
        "message": "Subject assigned successfully"
    }

@router.get("/{subject_id}/students", response_model=AllUserResponse)
def students_by_subject(subject_id: int, db = Depends(get_db), user = Depends(PermissionCheck("view subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    return {"users": subject.students}

@router.delete("/{subject_id}/student/{student_id}")
def revoke_subject(subject_id: int, student_id: int, db = Depends(get_db), user = Depends(PermissionCheck("revoke subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    student = db.get(User, student_id)
    if not student or "student" not in student.role_name:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    if subject not in student.subjects:
        raise HTTPException(
            status_code=422,
            detail="Subject not assigned to this student"
        )

    student.subjects.remove(subject)
    db.commit()

    return {
        "status":True,
        "message": "Subject revoked successfully"
    }

@router.post("/{subject_id}/teacher/{teacher_id}")
def assign_subject_to_teacher(subject_id: int, teacher_id: int, db = Depends(get_db), user = Depends(PermissionCheck("assign teacher subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    teacher = db.get(User, teacher_id)
    if not teacher or "teacher" not in teacher.role_name:
        raise HTTPException(
            status_code=404,
            detail="teacher not found"
        )

    if subject in teacher.taught_subjects:
        raise HTTPException(
            status_code=422,
            detail="Subject already assigned to this teacher"
        )

    teacher.taught_subjects.append(subject)
    db.commit()

    return {
        "status":True,
        "message": "Subject assigned to teacher successfully"
    }

@router.get("/{subject_id}/teachers", response_model=AllUserResponse)
def teachers_by_subject(subject_id: int, db = Depends(get_db), user = Depends(PermissionCheck("view subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    return {"users": subject.teachers}

@router.delete("/{subject_id}/teacher/{teacher_id}")
def revoke_subject_from_teacher(subject_id: int, teacher_id: int, db = Depends(get_db), user = Depends(PermissionCheck("revoke teacher subject"))):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    teacher = db.get(User, teacher_id)
    if not teacher or "teacher" not in teacher.role_name:
        raise HTTPException(
            status_code=404,
            detail="teacher not found"
        )

    if subject not in teacher.taught_subjects:
        raise HTTPException(
            status_code=422,
            detail="Subject not assigned to this teacher"
        )

    teacher.taught_subjects.remove(subject)
    db.commit()

    return {
        "status":True,
        "message": "Subject revoked from teacher successfully"
    }
