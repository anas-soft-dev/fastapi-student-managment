from fastapi import FastAPI
from app.database import Base,engine
import app.models.user 
import app.models.role

from app.routers.authentication import router as auth_router
from app.routers.teacher import router as teacher_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(teacher_router)

Base.metadata.create_all(engine)