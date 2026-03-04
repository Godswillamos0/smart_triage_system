from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models import (
    Tickets,
    TicketPriority,
    TicketStatus,
    TicketCategory,
)


class TicketStatusRequest(BaseModel):
    status: TicketStatus


class TicketPriorityRequest(BaseModel):
    priority: str


class TicketCategoryRequest(BaseModel):
    category: str


class CreateTicketRequest(BaseModel):
    title: str
    description: str
    

class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    category: str

    class Config:
        from_attributes = True
