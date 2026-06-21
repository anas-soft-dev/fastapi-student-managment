from passlib.context import CryptContext
from fastapi import Depends, HTTPException
import jwt
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer

import os
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.user import User
load_dotenv()

session = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

exp_time = os.getenv("JWT_EXPIRE_TIME",30)
secret_key = os.getenv("JWT_SECRET_KEY")
algorithm = os.getenv("JWT_ALGORITHM","HS256")

crypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated = "auto"
)

def make_hash(pwd: str) -> str:
    return crypt_context.hash(pwd)

def verify_hash(pwd: str, hash_pwd) -> bool:
    return crypt_context.verify(pwd, hash_pwd)

def create_access_token(data:dict)->str:
    payload = data.copy()

    exp = datetime.now(timezone.utc) + timedelta(
        minutes=int(exp_time)
    )

    payload["exp"] = exp

    return jwt.encode(
        payload,
        secret_key,
        algorithm
    )

def get_current_user(db=Depends(get_db),cred: HTTPAuthorizationCredentials = Depends(session)) -> User:
    token = cred.credentials

    try:
        data = jwt.decode(
            token,
            secret_key,
            algorithm
        )

        user = db.get(User,data["id"])

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token Expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="invalid token"
        )

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:

        intersection = list(set(self.allowed_roles).intersection(user.role_name))
        print(intersection)
        # check = False
        # for role in user.roles:
        #     if role.name in self.allowed_roles:
        #         check = True
        #         break

        if len(intersection) == 0:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission for this resource",
            )
        return user


class PermissionCheck():
    def __init__(self, permission):
        self.permission = permission

    def __call__(self, user = Depends(get_current_user)):
        if not self.permission in user.permissions:
            raise HTTPException(
                status_code=401,
                detail="permission denied"
            )
        return user