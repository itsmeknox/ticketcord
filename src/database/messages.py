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

