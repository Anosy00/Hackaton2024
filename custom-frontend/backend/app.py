from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from chainlit.auth import create_jwt
from chainlit.user import User
from chainlit.utils import mount_chainlit

from dotenv import load_dotenv
import boto3

from fastapi import FastAPI, Depends

from models import Session, get_db

from database import CRUDMessage, CRUDConversation, CRUDUser

load_dotenv()

client = boto3.client("bedrock", region_name="us-east-1")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/custom-auth")
async def custom_auth( ):
    token = create_jwt(User(identifier="Test User"))
    return JSONResponse({"token": token})


class PromptRequest(BaseModel):
    prompt: str


@app.post("/users/")
def create_user(email: str, username: str, password: str, db: Session = Depends(get_db)):
    user_crud = CRUDUser(db)
    user = user_crud.create(email=email, username=username, password=password)
    print("Je passe par le crud")
    return {"user_id": user.id, "email": user.email, "username": user.username}


@app.post("/conversations/{user_id}")
def start_conversation(user_id: int, db: Session = Depends(get_db)):
    conversation_crud = CRUDConversation(db)
    conversation = conversation_crud.create(user_id=user_id)
    return {"conversation_id": conversation.conversation_id, "created_at": conversation.created_at}


@app.post("/conversations/{conversation_id}/messages")
def post_message(conversation_id: int, sender: str, message_content: str, db: Session = Depends(get_db)):
    message_crud = CRUDMessage(db)
    message = message_crud.add(conversation_id=conversation_id, sender=sender, message_content=message_content)
    return {"message_id": message.message_id, "timestamp": message.timestamp}


@app.get("/get_user/")
def get_user(email: str, db: Session = Depends(get_db)):
    user_crud = CRUDUser(db)
    user = user_crud.get_by_email(email=email)
    return {"user_id": user.id, "email": user.email, "username": user.username}



mount_chainlit(app=app, target="cl_app.py", path="/chainlit")
