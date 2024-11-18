from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Literal, Optional
from datetime import datetime, timezone
from .helper import generate_unique_id

TICKET_STATUS = ["ACTIVE", "CLOSED", "DELETED"]

class PostTicketPayload(BaseModel):
    title: str
    description: str

# Ticket model
class TicketUser(BaseModel):
    id: int = Field(default_factory=generate_unique_id)
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
    last_seen_message_id: Optional[int] = None
    is_resolved: bool = False
    webhook_url: str
    status: Literal["ACTIVE", "DELETED", "CLOSED", "PENDING"]
    messages: list = []


# Message
class PostMessagePayload(BaseModel):
    content: str

class MessageUser(BaseModel):
    id: int = Field(default_factory=generate_unique_id)
    username: str

class Message(BaseModel):
    id: int = Field(default_factory=generate_unique_id)
    ticket_id: int
    content: str
    user: MessageUser
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_read: bool = False
    attachments: list = []