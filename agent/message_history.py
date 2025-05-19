from typing import Any
from langchain_core.messages import HumanMessage, AIMessage

from database.database_functions import add_message_to_existing_session, load_session_messages

class MessageHistoryFromPostgres:
    session_id: str
    messages: list[str]

    def __init__(self, session_id: str, messages: list[str]) -> None:
        self.session_id = session_id
        self.messages = messages

    def get_session_history(self, session_id: str) -> list[str]:
        return self.messages
    
    def add_messages(self, new_messages: list[Any]) -> None:
        for message in new_messages:
            if isinstance(message, HumanMessage):
                add_message_to_existing_session(session_id=self.session_id, sender="User", text=message.content)
            elif isinstance(message, AIMessage):
                add_message_to_existing_session(session_id=self.session_id, sender="AI", text=message.content)
        self.messages += new_messages
        

def get_message_history(session_id: int) -> MessageHistoryFromPostgres:
    messages_from_database = load_session_messages(session_id)

    if not messages_from_database:
        return MessageHistoryFromPostgres(session_id=session_id, messages=[])
    
    messages = []
    for sender, text in messages_from_database:
        if sender == "User":
            messages.append(HumanMessage(content=text, additional_kwargs={}, response_metadata={}))
        else:
            messages.append(AIMessage(content=text, additional_kwargs={}, response_metadata={}))
        return MessageHistoryFromPostgres(session_id=session_id, messages=messages)