from sqlalchemy.orm import Session
from models import User, Conversation, Message

class CRUDUser:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, email: str, username: str, password: str) -> User:
        user = User(email=email, username=username, password=password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def delete(self, user_id: int) -> bool:
        user = self.get(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

class CRUDConversation:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, user_id: int) -> Conversation:
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get(self, conversation_id: int) -> Conversation:
        return self.db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()

    def get_all_by_user(self, user_id: int):
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).all()

class CRUDMessage:
    def __init__(self, db_session: Session):
        self.db = db_session

    def add(self, conversation_id: int, sender: str, message_content: str) -> Message:
        message = Message(conversation_id=conversation_id, sender=sender, message_content=message_content)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_all_by_conversation(self, conversation_id: int):
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).all()


