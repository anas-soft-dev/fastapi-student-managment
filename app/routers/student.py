from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.user import User
from app.schemas.user import AllUserResponse, UserRegisterSchema, UserResponse
from app.models.role import Role
from app.auth import PermissionCheck

router = APIRouter(prefix="/student", tags=["Student"])

@router.get("",response_model=AllUserResponse)
def view(db = Depends(get_db), user = Depends(PermissionCheck("view student"))):
    users = db.query(User).join(User.roles).filter(Role.name == "student").all()
    return {"users":users}

@router.post("",response_model=UserResponse)
def store(data: UserRegisterSchema, db=Depends(get_db), user = Depends(PermissionCheck("add student"))):
    exist_user = db.query(User).where(User.email == data.email).first()
    if exist_user:
        raise HTTPException(
            status_code=422,
            detail="Email already Exists"
        )
    user = User(**data.model_dump())

    role = db.query(Role).where(Role.name == "student").first()
    user.assign_role(role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{student_id}", response_model=UserResponse)
def update(student_id: int, data: UserRegisterSchema, db = Depends(get_db), user = Depends(PermissionCheck("edit student"))):
    user = db.get(User, student_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )

    user.name = data.name
    user.email = data.email
    user.password = data.password

    db.commit()
    db.refresh(user)

    return user

@router.delete("/{student_id}")
def delete(student_id:int, db= Depends(get_db), user = Depends(PermissionCheck("delete student"))):
    user = db.get(User, student_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )

    db.delete(user)
    db.commit()

    return {
        "status":True,
        "message": "Successfully deleted"
    }
