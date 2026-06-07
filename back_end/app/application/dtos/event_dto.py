from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel
from app.domain.entities.event import EventStatus


class EventCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = None
    capacity: int


class EventUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[EventStatus] = None


class EventDTO(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = None
    capacity: int
    registered_count: int
    status: EventStatus
    created_by: uuid.UUID
    created_at: datetime

class PaginatedEventsDTO(BaseModel):
    items: list[EventDTO]
    total: int
    page: int
    limit: int
    pages: int