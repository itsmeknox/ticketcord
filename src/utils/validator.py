from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Literal
from datetime import datetime, timezone
from .helper import generate_unique_id

TICKET_STATUS = ["ACTIVE", "CLOSED", "DELETED"]

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
    id: int = Field(default_factory=generate_unique_id)
    title: str
    description: str
    user: TicketUser
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen_message_id: int | None
    status: Literal["ACTIVE", "DELETED", "CLOSED", "PENDING"]