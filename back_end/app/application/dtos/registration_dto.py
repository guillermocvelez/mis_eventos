from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class RegistrationDTO(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID
    registered_at: datetime


class EventRegistrantDTO(BaseModel):
    user_id: UUID
    email: str
    role: str
    registered_at: datetime
