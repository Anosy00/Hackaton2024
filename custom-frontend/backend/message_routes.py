from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import CRUDMessage
from models import get_db

message_router = APIRouter()


@message_router.post("/{conversation_id}/messages")
def post_message(conversation_id: int, sender: str, message_content: str, db: Session = Depends(get_db)):
    message_crud = CRUDMessage(db)
    message = message_crud.add(conversation_id=conversation_id, sender=sender, message_content=message_content)
    return {"message_id": message.message_id, "timestamp": message.timestamp}


@message_router.post("/conversations/{conversation_id}/messages")
def post_message(conversation_id: int, sender: str, message_content: str, db: Session = Depends(get_db)):
    message_crud = CRUDMessage(db)
    message = message_crud.add(conversation_id=conversation_id, sender=sender, message_content=message_content)
    return {"message_id": message.message_id, "timestamp": message.timestamp}