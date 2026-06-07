from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SessionCreateDTO(BaseModel):
    title: str
    speaker: Optional[str] = None
    start_time: datetime
    end_time: datetime
    capacity: Optional[int] = None


class SessionUpdateDTO(BaseModel):
    title: Optional[str] = None
    speaker: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = None


class SessionDTO(BaseModel):
    id: UUID
    event_id: UUID
    title: str
    speaker: Optional[str] = None
    start_time: datetime
    end_time: datetime
    capacity: Optional[int]
    registered_count: int