from utils.schema import Ticket
from typing_extensions import List
from utils.mongo_client import get_database

db = get_database()



def insert_ticket(data: Ticket):
    return db["tickets"].insert_one(data.model_dump())


def get_ticket(ticket_id: int):
    return db["tickets"].find_one({"id": ticket_id})


def get_tickets_by_user_id(user_id: int, status: List[str]=None) -> List[Ticket]:
    ...
