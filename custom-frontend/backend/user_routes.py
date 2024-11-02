from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import CRUDUser  # Assure-toi que tu as un fichier database.py avec cette fonction
from models import get_db

user_router = APIRouter()


@user_router.post("/")
def create_user(email: str, username: str, password: str, db: Session = Depends(get_db)):
    user_crud = CRUDUser(db)
    user = user_crud.create(email=email, username=username, password=password)
    return {"user_id": user.id, "email": user.email, "username": user.username}


@user_router.get("/{email}")
def get_user(email: str, db: Session = Depends(get_db)):
    user_crud = CRUDUser(db)
    user = user_crud.get_by_email(email=email)
    return {"user_id": user.id, "email": user.email, "username": user.username}


@user_router.post("/create_users/")
def create_user(email: str, username: str, password: str, db: Session = Depends(get_db)):
    user_crud = CRUDUser(db)
    user = user_crud.create(email=email, username=username, password=password)
    return {"user_id": user.id, "email": user.email, "username": user.username}


@user_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_crud = CRUDUser(db)
    success = user_crud.delete(user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}