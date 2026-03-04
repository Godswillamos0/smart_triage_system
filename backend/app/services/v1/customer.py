from fastapi import HTTPException
from app.schemas.tickets import (
    CreateTicketRequest
)
from app.agent.analyze import analyze_ticket
from app.db.dependencies import db_dependency
from app.db.models import (
    Tickets,
    TicketPriority,
    TicketStatus,
    TicketCategory,
)


async def create_ticket(ticket: CreateTicketRequest, db: db_dependency):
    # ai categorize
    data = analyze_ticket(ticket.title, ticket.description)

    try:
        category = TicketCategory(data.get("category"))
    except ValueError:
        category = TicketCategory.other

    try:
        priority = TicketPriority(data.get("priority"))
    except ValueError:
        priority = TicketPriority.low

    ticket_model = Tickets(
        title=ticket.title,
        description=ticket.description,
        category=category,
        priority=priority,
        status=TicketStatus.open
    )

    try:
        db.add(ticket_model)
        db.commit()
        db.refresh(ticket_model)
        return ticket_model
    except Exception as e:
        db.rollback()
        print(f"DATABASE ERROR: {e}") 
        raise HTTPException(status_code=500, detail="Internal Server Error")