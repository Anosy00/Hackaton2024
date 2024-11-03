from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import CRUDConversation
from models import get_db
from memory_management import memory

conversation_router = APIRouter()


@conversation_router.post("/conversations/{user_id}")
def start_conversation(user_id: int, db: Session = Depends(get_db)):
    conversation_crud = CRUDConversation(db)
    conversation = conversation_crud.create(user_id=user_id)
    return {"conversation_id": conversation.conversation_id, "created_at": conversation.created_at}

@conversation_router.get("/conversation_id")
def get_conversation_id(user_id: int, db: Session = Depends(get_db)):
    conversation_crud = CRUDConversation(db)
    conversation = conversation_crud.create(user_id=user_id)
    return {"conversation_id": conversation.conversation_id, "created_at": conversation.created_at}



@conversation_router.get("/get_conversation/{conversation_id}")
def get_conversation(conversation_id: int, user_id: int , db: Session = Depends(get_db)):
    conversation_crud = CRUDConversation(db)
    conversation = conversation_crud.get(user_id=user_id)
    messages = conversation_crud.get_all_messages(conversation_id)
    conversation_history = [{"is_bot": msg.is_bot, "content": msg.content} for msg in messages]

    # load into LangChain memory for context
    for msg in conversation_history:
        if msg["is_bot"] == False:
            memory.add_user_message(msg["content"])
        else:
            memory.add_ai_message(msg["content"])

    return {"conversation_history": conversation_history}