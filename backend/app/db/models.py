from decimal import Decimal
import uuid
import time
import random
from sqids import Sqids
from enum import Enum
from sqlalchemy import (
    Column,
    func,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Float,
    Time,
    DateTime,
    Numeric,
    Enum as DbEnum,
    Date,
    event
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import PickleType
from sqlalchemy.orm import relationship

from .database import Base

sqids = Sqids(min_length=10)


class TicketCategory(str, Enum):
    billing = "billing"
    technical_bug = "technical_bug"
    feature_request = "feature_request"
    other = "other"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    

class TicketPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    



class Tickets(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True, default=lambda: sqids.encode([int(time.time() * 1000), random.randint(0, 100)]))
    category = Column(DbEnum(TicketCategory), default = TicketCategory.other)
    status = Column(DbEnum(TicketStatus), default = TicketStatus.open)
    priority = Column(DbEnum(TicketPriority), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)


class SupportAgent(Base):
    __tablename__ = "support_agents"

    id = Column(String, primary_key=True, index=True, default=lambda: sqids.encode([int(time.time() * 1000), random.randint(0, 100)]))
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)



    
