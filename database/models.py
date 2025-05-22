from typing import List, Optional
from datetime import date, datetime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Text

class Message(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str
    text: str
    session_id: Optional[int] = Field(default=None, foreign_key="usersession.id")
    session: Optional["UserSession"] = Relationship(back_populates="messages")


class UserSession(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True)
    name: str
    messages: List[Message] = Relationship(back_populates="session")
    user_id: Optional[int] = Field(default=None, foreign_key="appuser.id")
    user: Optional["AppUser"] = Relationship(back_populates="sessions")


class AppUser(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int = Field(default=None, primary_key=True)
    username: str
    password: str
    access_token: Optional[str] = Field(default=None, sa_type=Text)
    access_token_expiration: Optional[datetime] = None
    sessions: List["UserSession"] = Relationship(back_populates="user")