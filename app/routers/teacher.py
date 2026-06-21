from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.user import User
from app.schemas.user import AllUserResponse, UserRegisterSchema, UserResponse
from app.models.role import Role
from app.auth import PermissionCheck

router = APIRouter(prefix="/teacher", tags=["Teacher"])

@router.get("",response_model=AllUserResponse)
def view(db = Depends(get_db), user = Depends(PermissionCheck("view teacher"))):
    users = db.query(User).join(User.roles).filter(Role.name == "teacher").all()
    return {"users":users}

@router.post("",response_model=UserResponse)
def store(data: UserRegisterSchema, db=Depends(get_db), user = Depends(PermissionCheck("add teacher"))):
    exist_user = db.query(User).where(User.email == data.email).first()
    if exist_user:
        raise HTTPException(
            status_code=422,
            detail="Email already Exists"
        )
    # teacher_role = db.query(Role).where(Role.name == "teacher").first()
    user = User(**data.model_dump())

    role = db.query(Role).where(Role.name == "teacher").first()
    user.assign_role(role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{teacher_id}", response_model=UserResponse)
def update(teacher_id: int, data: UserRegisterSchema, db = Depends(get_db), user = Depends(PermissionCheck("edit teacher"))):
    user = db.get(User, teacher_id)

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

@router.delete("/{teacher_id}")
def delete(teacher_id:int, db= Depends(get_db), user = Depends(PermissionCheck("delete teacher"))):
    user = db.get(User, teacher_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )
    # db.query(User).filter(User.id == teacher_id).delete()
    
    db.delete(user)
    db.commit()

    return {
        "status":True,
        "message": "Successfully deleted"
    }