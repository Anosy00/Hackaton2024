from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

# Define the base class
Base = declarative_base()

# Database setup
engine = create_engine('sqlite:///test_database.db')
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    password = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class Conversation(Base):
    __tablename__ = "conversations"
    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"))
    sender = Column(String)
    message_content = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))


# Create tables
Base.metadata.create_all(bind=engine)

# Start session and add data
#session = Session()
#user1 = User(id=1, email="test@gmail.com", username="test")
#session.add_all([user1])
#session.commit()

# Query users
#users = session.query(User).all()
#for user in users:
#    print(user)
