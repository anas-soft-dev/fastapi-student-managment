from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserRegisterSchema, UserLoginSchema, UserResponse, LoginResponse
from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.auth import make_hash, verify_hash, create_access_token,get_current_user, RoleChecker, PermissionCheck


router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(data: UserRegisterSchema, db = Depends(get_db)):
    role = db.query(Role).filter(Role.name == "student").first()

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=422,
            detail="Email Already Exists"
        )
    # print(type(teacher_role))

    # return teacher_role

    user = User(
        name = data.name,
        email = data.email,
        password = make_hash(data.password)
    )

    user.roles.append(role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=LoginResponse)
def login(cred: UserLoginSchema, db = Depends(get_db)):
    user  = db.query(User).filter(User.email == cred.email).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="invalid email"
        )
    
    if not verify_hash(cred.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="invalid password"
        )
    
    token = create_access_token({"id":user.id})

    return {
        "access_token":token,
        "token_type": "Bearer"
    }

@router.get("/profile", response_model=UserResponse)
def profile(user = Depends(PermissionCheck("view profile"))):
    return user
    

from fastapi import Form, UploadFile, File
import uuid
@router.post("/profile-image")
async def update_profile(name = Form(),image: UploadFile = File(...),user = Depends(PermissionCheck("update profile")), db = Depends(get_db)):
    filename = f"{uuid.uuid4()}_{image.filename}"
    path =  f"upload/{filename}"

    with open(path,"wb") as buffer:
        data = await image.read()
        buffer.write(data)

    user.name = name
    user.image = path
    db.commit()
    db.refresh(user)

    return user

    
