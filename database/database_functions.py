from sqlmodel import Session as DBSession, delete, select
from database.database import engine
from database.models import UserSession, Message


def create_session(name: str) -> int:
    session = UserSession(name=name)

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
    

def get_all_sessions_from_db() -> dict[str,int]:
    """Return dict of session_name→session_id"""
    with DBSession(engine) as db:
        rows = db.exec(select(UserSession)).all()
    return {row.name: row.id for row in rows}