from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import CRUDConversation
from models import get_db

conversation_router = APIRouter()


@conversation_router.post("/conversations/{user_id}")
def start_conversation(user_id: int, db: Session = Depends(get_db)):
    conversation_crud = CRUDConversation(db)
    conversation = conversation_crud.create(user_id=user_id)
    return {"conversation_id": conversation.conversation_id, "created_at": conversation.created_at}


