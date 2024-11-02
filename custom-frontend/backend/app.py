from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from chainlit.auth import create_jwt
from chainlit.user import User
from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from botoApi import invoke_bedrock_model
import chainlit as cl
from dotenv import load_dotenv

@cl.on_message
async def main(message):
    response = invoke_bedrock_model(message.content)
    await cl.Message(content=response).send()



load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/custom-auth")
async def custom_auth():
    # Verify the user's identity with custom logic.
    token = create_jwt(User(identifier="Test User"))
    return JSONResponse({"token": token})

mount_chainlit(app=app, target="cl_app.py", path="/chainlit")



app = FastAPI()

@app.post("/predict/")
async def predict(input_data: dict):
    # Remplacez 'mon_model' par l'ID du modèle sur AWS Bedrock
    model_id = "mon_model"
    result = invoke_bedrock_model(model_id, input_data)
    return {"prediction": result}
