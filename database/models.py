from typing import List, Optional
from datetime import date
from sqlmodel import Field, Relationship, SQLModel

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