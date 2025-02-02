from utils.mongo_client import get_database

from utils.schema import (
    Message
)


from modules.decorator import database_error_handler


message_collection = get_database()['messages']


@database_error_handler
def insert_message(data: Message):
    result = message_collection.insert_one(
        data.model_dump()
    )
    return result

@database_error_handler
def fetch_messages(ticket_id: int) -> list[Message]:
    query = {
        'ticket_id': ticket_id
    }
    result = message_collection.find(query)
    return [Message(**data) for data in result]


@database_error_handler
def update_message_content(ticket_id: str, message_id: str, content: str) -> Message:
    if not isinstance(content, str):
        raise ValueError("content must be a string")
        
    query = {
        'id': str(message_id),
        'ticket_id': str(ticket_id)
    }
    data = message_collection.find_one_and_update(
        query,
        {'$set': {'content': content}},
        return_document=True
        
    )
    if data:
        return Message(**data)
    
    return None


@database_error_handler
def delete_message(message_id: str):
    query = {
        'id': str(message_id)
    }
    data = message_collection.find_one_and_delete(query)
    if data:
        return Message(**data)
    return None

        