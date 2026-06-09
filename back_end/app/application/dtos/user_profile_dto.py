import uuid
from datetime import datetime
from pydantic import BaseModel

class UserProfileDTO(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    created_at: datetime
    is_active: bool
    organized_count: int
    registered_count: int