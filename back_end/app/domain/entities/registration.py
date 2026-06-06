import uuid
from datetime import datetime
from pydantic import BaseModel


class Registration(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID
    registered_at: datetime