import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    admin = "admin"
    organizer = "organizer"
    attendee = "attendee"


class User(BaseModel):
    id: uuid.UUID
    email: str
    hashed_password: str
    role: UserRole = UserRole.attendee
    is_active: bool = True
    created_at: datetime

    def has_role(self, role: str) -> bool:
        return self.role == role