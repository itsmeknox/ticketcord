from pydantic import BaseModel, EmailStr


class PostTicketUserPayload(BaseModel):
    username: str
    email: EmailStr


class PostTicketPayload(BaseModel):
    title: str
    description: str
    user: PostTicketUserPayload | None
