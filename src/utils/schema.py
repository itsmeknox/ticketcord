from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional
from .helper import generate_snowflake_id, generate_timestamp
from .enums import UserRole, TicketStatus, SupportRole, IssueLevel

# Database Schema
class TicketUser(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    
# User Model
class User(BaseModel):
    id: str = Field(default_factory=generate_snowflake_id, description="Unique user ID")
    username: str = Field(..., min_length=3, max_length=50, description="User's username")
    email: EmailStr = Field(..., description="User's email address")
    role: UserRole = Field(UserRole.CUSTOMER, description="User role: CUSTOMER, AGENT, or ADMIN")
    created_at: int = Field(default_factory=generate_timestamp, description="User creation timestamp")
    updated_at: int = Field(default_factory=generate_timestamp, description="User update timestamp")


# Ticket Model
class Ticket(BaseModel):
    # id: int = Field(default_factory=generate_snowflake_id, description="Unique ticket ID")
    id: str = Field(..., description="Unique identifier for the Discord channel/thread associated with the ticket")

    user_id: str = Field(..., description="ID of the user who raised the ticket")
    user_email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="User's username")


    user_role: UserRole = Field(UserRole.CUSTOMER, description="User role: CUSTOMER, AGENT, or ADMIN")
    topic: Optional[str] = Field(None, description="Ticket topic/title")
    description: Optional[str] = Field(None, description="Detailed description of the ticket")
    status: TicketStatus = Field(TicketStatus.ACTIVE, description="Status of the ticket: ACTIVE, CLOSED or DELETED")
    webhook_url: str = Field(..., description="Webhook URL for the ticket channel")
    created_at: int = Field(default_factory=generate_timestamp, description="Ticket creation timestamp")
    updated_at: int = Field(default_factory=generate_timestamp, description="Ticket update timestamp")

    support_role: SupportRole = Field(SupportRole.GENERAL, description="Support role assigned to the ticket")
    issue_level: IssueLevel = Field(IssueLevel.NORMAL, description="Issue level of the ticket")

# Message Model
class Message(BaseModel):
    id: str = Field(default_factory=generate_snowflake_id, description="Unique message ID")
    ticket_id: str = Field(..., description="Associated ticket ID")
    author_id: str = Field(..., description="ID of the user who sent the message")
    author_name: str = Field(..., min_length=2, max_length=50, description="Username of the message sender")
    content: str = Field(..., description="Message content")
    attachments: List[str] = Field(default_factory=list, description="List of attachment URLs")
    created_at: int = Field(default_factory=generate_timestamp, description="Message sent timestamp")
    updated_at: int = Field(default_factory=generate_timestamp, description="Message update timestamp")



#  ============== API Request ==============

class CreateTicketRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic of the ticket")
    description: Optional[str] = Field(None, description="Detailed description of the issue")


class UpdateTicketStatusRequest(BaseModel):
    status: TicketStatus = Field(..., description="New status for the ticket: ACTIVE, CLOSED or DELETED")


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Message content")
    attachments: List[HttpUrl] = Field(default_factory=list, description="List of attachment URLs")



# ============== API Response ==============
class TicketResponse(BaseModel):
    id: str
    user_id: str
    topic: Optional[str]
    description: Optional[str]
    status: TicketStatus
    created_at: int
    updated_at: int

    user_role: UserRole
    support_role: SupportRole
    issue_level: IssueLevel 


class TicketsResponse(BaseModel):
    tickets: List[TicketResponse]
    

class MessageResponse(BaseModel):
    id: str
    ticket_id: str
    author_id: str
    author_name: str
    content: str
    attachments: List[HttpUrl]
    created_at: int
    updated_at: int

class MessagesResponse(BaseModel):
    messages: List[MessageResponse]
    
