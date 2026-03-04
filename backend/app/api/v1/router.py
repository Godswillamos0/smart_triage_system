from fastapi import APIRouter
from .auth import router as auth_router
from .ticket import router as ticket_router
from .customer import router as customer_router


endpoint = APIRouter(
    prefix="/api/v1"
)

endpoint.include_router(auth_router)
endpoint.include_router(ticket_router)
endpoint.include_router(customer_router)