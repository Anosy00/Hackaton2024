from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from chainlit.auth import create_jwt
from chainlit.user import User
from chainlit.utils import mount_chainlit

from dotenv import load_dotenv
import boto3

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from jwt_auth import get_current_user, authenticate_user, create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_user_username = "testuser"
fake_user_password_hashed = pwd_context.hash("testpassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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
async def custom_auth(current_user: dict = Depends(get_current_user)):
    # Génère un token JWT pour l'utilisateur
    token = create_jwt(User(identifier="Test User"))
    return JSONResponse({"token": token})

@app.get("/")
async def custom_auth(current_user: dict = Depends(get_current_user)):
    # Génère un token JWT pour l'utilisateur
    print("current_user")
    return "current_user"


class PromptRequest(BaseModel):
    prompt: str


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    print(current_user)
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


mount_chainlit(app=app, target="cl_app.py", path="/chainlit")
