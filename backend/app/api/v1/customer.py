from fastapi import APIRouter
from app.schemas.tickets import (
    CreateTicketRequest,
    TicketResponse
)
from app.services.v1.customer import create_ticket


router = APIRouter(
    prefix="/customer",
    tags=["Customer"]
)


router.post("/ticket", response_model=TicketResponse)(create_ticket)
