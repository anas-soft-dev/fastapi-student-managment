from fastapi import APIRouter, Depends
from app.schemas.user import UserRegisterSchema
from app.database import get_db
from app.models.user import User
from app.auth import make_hash, verify_hash


router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register")
def register(data: UserRegisterSchema, db = Depends(get_db)):
    
    user = User(
        name = data.name,
        email = data.email,
        role= data.role,
        password = make_hash(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login():
   return verify_hash("1234567","$2b$12$zrSmCFIRU5UxQT8/VfWsKeeuBGqCvAs0yzVtmO18tqmxEwpF6oTlS")
