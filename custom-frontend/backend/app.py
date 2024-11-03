import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from fastapi import UploadFile, File
from starlette.responses import JSONResponse
import chainlit as cl
from chainlit.utils import mount_chainlit

from dotenv import load_dotenv
import boto3

from fastapi import FastAPI

from user_routes import user_router
from message_routes import message_router
from conversation_routes import conversation_router

load_dotenv()

client = boto3.client("bedrock", region_name="us-west-2")

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(conversation_router, prefix="/conversations", tags=["conversations"])
app.include_router(message_router, prefix="/messages", tags=["messages"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


mount_chainlit(app=app, target="cl_app.py", path="/chainlit")
