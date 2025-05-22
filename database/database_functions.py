from datetime import datetime, timedelta
import random
import string
import bcrypt
from sqlmodel import Session as DBSession, delete, select
from database.database import engine
from database.models import AppUser, UserSession, Message


def create_session(name: str, access_token: str) -> int:
    user = validate_access_token(access_token)
    session = UserSession(name=name, user_id=user.id)

    with DBSession(engine) as db:
        db.add(session)         
        db.commit()
        db.refresh(session)   

    print(f"Created Session with ID: {session.id}")
    return session.id


def get_default_session_id() -> int:
    with DBSession(engine) as db:
        default_session_id = db.exec(
            select(UserSession.id).where(UserSession.name == "Default")
        ).first()
        return default_session_id
    

def delete_session(session_id: int) -> None:
    with DBSession(engine) as db:
        db.exec(delete(Message).where(Message.session_id == session_id))
        db.exec(delete(UserSession).where(UserSession.id == session_id))
        db.commit()


def add_message_to_existing_session(session_id: int, sender: str, text: str) -> None:
    with DBSession(engine) as db:
        session = db.exec(select(UserSession).where(UserSession.id == session_id)).first()

        if not session:
            print(f"Session with ID {session_id} not found.")
            return

        new_message = Message(sender=sender, text=text, session_id=session_id)

        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        print(f"Added message to session {session_id}: {sender} says '{text}'")


def load_session_messages(session_id: int) -> list[tuple[str, str]]:
    with DBSession(engine) as db:
        db_sess = db.exec(
            select(UserSession).where(UserSession.id == session_id)
        ).first()
        if not db_sess:
            return []
        
        return [(msg.sender, msg.text) for msg in db_sess.messages]
    

def delete_session_messages(session_id: int) -> None:
    with DBSession(engine) as db:
        db.exec(delete(Message).where(Message.session_id == session_id))
        db.commit()
    

def get_sessions_for_user(access_token: str) -> dict[str, int]:
    """Return dict of session_name → session_id for a given user_id"""
    user = validate_access_token(access_token)
    with DBSession(engine) as db:
        rows = db.exec(
            select(UserSession).where(UserSession.user_id == user.id)
        ).all()
    return {row.name: row.id for row in rows}

    
def find_user_by_credentials(username: str, password: str) -> AppUser | None:
    """Securely authenticate a user by comparing the hashed password."""
    with DBSession(engine) as session:
        user = session.exec(select(AppUser).where(AppUser.username == username)).first()
        if not user:
            return None

        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):

            now = datetime.now()

            if user.access_token == None or user.access_token_expiration < now:
                user.access_token = ''.join(random.choices(string.ascii_letters + string.digits, k=256))
                user.access_token_expiration = now + timedelta(minutes=5)

                session.add(user)
                session.commit()
                session.refresh(user)

            return user
        
        return None

    

def validate_access_token(access_token: str) -> AppUser | None:
    now = datetime.now()
    with DBSession(engine) as session:
        user = session.exec(select(AppUser).where(AppUser.access_token == access_token)).first()
        if not user:
            return None
        elif user.access_token_expiration < now:
            return None
        else:
            return user