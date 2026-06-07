from uuid import UUID
from datetime import datetime
from typing import Optional
from app.application.dtos.speaker_dto import SpeakerDTO
from pydantic import BaseModel


class SessionCreateDTO(BaseModel):
    title: str
    speaker_id: Optional[UUID] = None
    start_time: datetime
    end_time: datetime
    capacity: Optional[int] = None


class SessionUpdateDTO(BaseModel):
    title: Optional[str] = None
    speaker_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = None


class SessionDTO(BaseModel):
    id: UUID
    event_id: UUID
    title: str
    speaker: Optional[SpeakerDTO] = None
    start_time: datetime
    end_time: datetime
    capacity: Optional[int]
    registered_count: int