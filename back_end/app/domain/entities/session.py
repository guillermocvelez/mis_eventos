import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventSession(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    title: str
    speaker: Optional[str] = None
    start_time: datetime
    end_time: datetime
    capacity: Optional[int] = None
    registered_count: int = 0

    def overlaps_with(self, other: "EventSession") -> bool:
        return self.start_time < other.end_time and self.end_time > other.start_time

    