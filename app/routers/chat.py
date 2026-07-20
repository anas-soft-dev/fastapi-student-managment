from fastapi import APIRouter, Depends
from app.chatbot.agent import run_agent
from app.schemas.chat import ChatInput, ChatOutput
from app.database import get_db
import uuid

router = APIRouter()


@router.post("/chat",response_model=ChatOutput)
def chat(data: ChatInput, db = Depends(get_db)):
    conversation_id = data.conversation_id
    if not conversation_id:
       conversation_id =  str(uuid.uuid4())
      
    reply = run_agent(db = db,message=data.message,conversation_id= conversation_id)
    return ChatOutput(reply=reply,conversation_id=conversation_id)


    