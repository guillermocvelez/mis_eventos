import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    admin = "admin"
    organizer = "organizer"
    attendee = "attendee"


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: str
    name: str
    hashed_password: str
    role: UserRole = UserRole.attendee
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def has_role(self, role: str) -> bool:
        return self.role == role