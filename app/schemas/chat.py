from pydantic import BaseModel

class ChatInput(BaseModel):
    message: str
    conversation_id: str

class ChatOutput(BaseModel):
    reply: str
    conversation_id: str