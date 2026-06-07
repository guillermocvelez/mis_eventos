from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class RegistrationDTO(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID
    registered_at: datetime