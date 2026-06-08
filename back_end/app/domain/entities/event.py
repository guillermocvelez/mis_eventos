import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from app.domain.entities.session import EventSession
from pydantic import BaseModel


class EventStatus(str, Enum):    
    draft = "draft"
    published = "published"
    cancelled = "cancelled"
    finished = "finished"


class Event(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    capacity: int
    registered_count: int = 0
    status: EventStatus = EventStatus.draft
    created_by: uuid.UUID
    created_at: datetime

    def has_capacity(self) -> bool:
        return self.registered_count < self.capacity

    def can_be_edited_by(self, user_id: uuid.UUID) -> bool:
        return self.created_by == user_id
    
    def session_is_within_range(self, session: "EventSession") -> bool:
            if self.end_date is None:
                return session.start_time.date() >= self.date.date()
            return session.start_time.date() >= self.date.date() and session.end_time.date() <= self.end_date.date()
