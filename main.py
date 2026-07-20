from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base,engine
import app.models.user
import app.models.role
import app.models.subject
import app.models.attendance

from app.routers.authentication import router as auth_router
from app.routers.teacher import router as teacher_router
from app.routers.student import router as student_router
from app.routers.subject import router as subject_router
from app.routers.attendance import router as attendance_router
from app.routers.chat import router as chat_router
import os
os.makedirs("upload", exist_ok=True)

app = FastAPI()

# CORS — allow the Next.js frontend to call the API (handles OPTIONS preflight).
# Set ALLOWED_ORIGINS in .env as a comma-separated list to add deployed frontends.
default_origins = "http://localhost:3000,http://127.0.0.1:3000"
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/upload", StaticFiles(directory="upload"), name="upload")

app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(subject_router)
app.include_router(attendance_router)
app.include_router(chat_router)

Base.metadata.create_all(engine)

@app.get("/home")
def home():
    return {"message": "Welcome to the Student Management System API!"}

# create_all() leaves a live connection in the pool. Under Passenger this module
# is imported in a parent process that then forks workers, so that socket would
# be shared by every child. Dispose it — each worker opens its own on demand.
engine.dispose()