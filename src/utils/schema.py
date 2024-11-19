from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional
from .helper import generate_snowflake_id, generate_timestamp
from .enums import UserRole, TicketStatus

# Database Schema

# User Model
class User(BaseModel):
    id: int = Field(default_factory=generate_snowflake_id, description="Unique user ID")
    username: str = Field(..., min_length=3, max_length=50, description="User's username")
    email: EmailStr = Field(..., description="User's email address")
    role: UserRole = Field(UserRole.CUSTOMER, description="User role: CUSTOMER, AGENT, or ADMIN")
    created_at: int = Field(default_factory=generate_timestamp, description="User creation timestamp")
    updated_at: int = Field(default_factory=generate_timestamp, description="User update timestamp")


# Ticket Model
class Ticket(BaseModel):
    id: int = Field(default_factory=generate_snowflake_id, description="Unique ticket ID")
    user_id: int = Field(..., description="ID of the user who raised the ticket")
    channel_id: int = Field(..., description="Unique identifier for the Discord channel/thread associated with the ticket")
    topic: Optional[str] = Field(None, description="Ticket topic/title")
    description: Optional[str] = Field(None, description="Detailed description of the ticket")
    status: TicketStatus = Field(TicketStatus.ACTIVE, description="Status of the ticket: ACTIVE, CLOSED or DELETED")
    created_at: int = Field(default_factory=generate_timestamp, description="Ticket creation timestamp")
    updated_at: int = Field(default_factory=generate_timestamp, description="Ticket update timestamp")


# Message Model
class Message(BaseModel):
    id: int = Field(default_factory=generate_snowflake_id, description="Unique message ID")
    ticket_id: int = Field(..., description="Associated ticket ID")
    sender_id: int = Field(..., description="ID of the user who sent the message")
    content: str = Field(..., description="Message content")
    attachments: List[HttpUrl] = Field(default_factory=list, description="List of attachment URLs")
    created_at: int = Field(default_factory=generate_timestamp, description="Message sent timestamp")
    updated_at: int = Field(default_factory=generate_timestamp, description="Message update timestamp")



#  ============== API Schema ==============

# API Request
class CreateTicketRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic of the ticket")
    description: Optional[str] = Field(None, description="Detailed description of the issue")


class UpdateTicketStatusRequest(BaseModel):
    status: TicketStatus = Field(..., description="New status for the ticket: ACTIVE, CLOSED or DELETED")


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Message content")
    attachments: List[HttpUrl] = Field(default_factory=list, description="List of attachment URLs")


# API Response
class TicketResponse(BaseModel):
    id: int
    user_id: int
    channel_id: int
    topic: Optional[str]
    description: Optional[str]
    status: TicketStatus
    created_at: int
    updated_at: int


class MessageResponse(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    content: str
    attachments: List[HttpUrl]
    created_at: int
    updated_at: int

class MessagesResponse(BaseModel):
    messages: List[MessageResponse]