import uuid
from datetime import datetime
from pydantic import BaseModel


class SessionRegistration(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    session_id: uuid.UUID
    registered_at: datetime