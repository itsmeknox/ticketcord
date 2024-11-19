from utils.mongo_client import get_database

from utils.schema import (
    Message
)

db = get_database()['messages']

def insert_message(data: Message):
    result = db.insert_one(
        data.model_dump()
    )
    return result

def fetch_messages(ticket_id: int) -> list[Message]:
    query = {
        'ticket_id': ticket_id
    }
    result = db.find(query)
    return [Message(**data) for data in result]
