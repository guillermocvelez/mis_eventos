import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint


class UserRole(str, Enum):
    admin = "admin"
    organizer = "organizer"
    attendee = "attendee"


class EventStatus(str, Enum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"
    finished = "finished"


class UserORM(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    role: UserRole = Field(default=UserRole.attendee)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EventORM(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = Field(default=None, max_length=255)
    capacity: int
    registered_count: int = Field(default=0)
    status: EventStatus = Field(default=EventStatus.draft)
    created_by: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EventSessionORM(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "event_sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="events.id")
    title: str = Field(max_length=255)
    speaker: Optional[str] = Field(default=None, max_length=255)
    start_time: datetime
    end_time: datetime
    capacity: Optional[int] = None
    registered_count: int = Field(default=0)


class RegistrationORM(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    event_id: uuid.UUID = Field(foreign_key="events.id")
    registered_at: datetime = Field(default_factory=datetime.utcnow)
