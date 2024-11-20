from utils.schema import Ticket
from utils.enums import TicketStatus
from typing_extensions import List  
from utils.mongo_client import get_database

ticket_collection = get_database()["tickets"]



def insert_ticket(ticket: Ticket) -> None:
    if not isinstance(ticket, Ticket):
        raise ValueError("ticket must be an instance of Ticket")
        
    return ticket_collection.insert_one(ticket.model_dump())


def fetch_ticket(ticket_id: str, user_id: str = None) -> Ticket:
    filter = {"id": str(ticket_id)}
    if user_id:
        filter["user_id"] = str(user_id)

    data = ticket_collection.find_one(filter)
    if data:
        return Ticket(**data)
    
    return None 


def fetch_user_tickets(user_id: str, status: List[TicketStatus]) -> List[Ticket]:
    # Convert status list to their string values for querying
    status_values = [s.value for s in status]

    # Build the query
    query = {
        "user_id": str(user_id),
        "status": {"$in": status_values}  # Match any of the provided statuses
    }

    # Execute the query
    cursor = ticket_collection.find(query)
    tickets: List[Ticket] = []
    for ticket in cursor:
        tickets.append(Ticket(**ticket))
    
    # Convert results to a list and return
    return tickets

def update_ticket_status(ticket_id: str, status: TicketStatus) -> Ticket:
    query = {"id": str(ticket_id)}
    update = {"$set": {"status": status.value}}
    result = ticket_collection.find_one_and_update(query, update, return_document=True)
    if not result:
        return None
    
    return Ticket(**result)



