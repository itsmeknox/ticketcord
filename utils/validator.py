from pydantic import BaseModel, EmailStr

from typing_extensions import Literal


TICKET_STATUS = Literal["ACTIVE", "CLOSED", "DELETED"]


__all__ = (
    "TICKET_STATUS",
    "PostTicketPayload",
    "Ticket",
)


# POST /tickets payload
class PostTicketUserPayload(BaseModel):
    username: str
    email: EmailStr


class PostTicketPayload(BaseModel):
    title: str
    description: str
    user: PostTicketUserPayload | None


# Ticket model
class TicketUser(BaseModel):
    username: str
    email: EmailStr
    is_authenticated: bool

class Ticket(BaseModel):
    id: int
    title: str
    description: str
    user: TicketUser
    created_at: str
    updated_at: str
    seen_message: int | None
    last_seen_message_id: int | None  # Add this line
    status: TICKET_STATUSnn