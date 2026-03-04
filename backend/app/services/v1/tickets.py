from fastapi import HTTPException, Query, status, Path
from typing import Optional
from app.db.dependencies import db_dependency
from app.db.models import (
    Tickets,
    TicketPriority,
    TicketStatus,
    TicketCategory,
)
from app.schemas.tickets import (
    CreateTicketRequest,
    TicketResponse,
    TicketStatusRequest,
    TicketPriorityRequest,
    TicketCategoryRequest
)

from .auth import user_cookie_dependency


async def get_tickets(
        user: user_cookie_dependency,
        db: db_dependency,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = Query(None),
        priority: Optional[str] = Query(None),
        category: Optional[str] = Query(None)
):
    """
        --  Get Ticket in list of 10
    """
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Tickets)

    if status:
        query = query.filter(Tickets.status == status)
    if priority:
        query = query.filter(Tickets.priority == priority)
    if category:
        query = query.filter(Tickets.category == category)

    tickets = query.offset(skip).limit(limit).all()
    return tickets


async def modify_ticket(
        user: user_cookie_dependency,
        db: db_dependency,
        status_data: TicketStatusRequest,
        ticket_id: str = Path(..., title="The ID of the ticket to modify"),
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    ticket_model = db.query(Tickets).filter(Tickets.id == ticket_id).first()
    
    if not ticket_model:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket_model.status == TicketStatus.resolved:
        raise HTTPException(status_code=400, detail="Ticket is already resolved")
    
    ticket_model.status = status_data.status
    
    db.commit()
    db.refresh(ticket_model)
    return ticket_model
    
    