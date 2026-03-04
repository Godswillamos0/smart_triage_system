from fastapi import APIRouter
from app.services.v1.tickets import (
    get_tickets,
    modify_ticket
)
from app.schemas.tickets import (
    CreateTicketRequest,
    TicketResponse,
    TicketStatusRequest,
    TicketPriorityRequest,
    TicketCategoryRequest
)


router = APIRouter(
    prefix="/ticket",
    tags=["Ticket"]
)

router.get("/ticket", response_model=list[TicketResponse])(get_tickets)
router.patch("/ticket/{ticket_id}", response_model=TicketResponse)(modify_ticket)