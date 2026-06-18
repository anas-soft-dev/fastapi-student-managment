from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserRegisterSchema, UserLoginSchema, UserResponse
from app.database import get_db, SessionLocal
from app.models.user import User
from app.auth import make_hash, verify_hash, create_access_token,get_current_user , create_user_jwt, RoleChecker


router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register")
def register(data: UserRegisterSchema, db = Depends(get_db)):
    
    user = User(
        name = data.name,
        email = data.email,
        role = data.role,
        password = make_hash(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
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
    
    token = create_access_token({"id":user.id,"role":user.role})

    return {
        "access_token":token,
        "token_type": "Bearer"
    }

@router.get("/profile", response_model=UserResponse)
def profile(user = Depends(RoleChecker("admin"))):
    return user

@router.get("/admin", response_model=UserResponse)
def admin(user = Depends(RoleChecker)):
    return user
    

    
