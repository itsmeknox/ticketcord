from utils.validator import Ticket
from typing_extensions import List, Literal



def insert_ticket(data: Ticket):
    ...

def get_ticket(ticket_id: int):
    ...

def get_tickets_by_user_id(user_id: int, status: List[str]) -> List[Ticket]:
    ...
