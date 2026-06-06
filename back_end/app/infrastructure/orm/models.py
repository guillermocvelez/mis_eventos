import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel


class UserORM(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__: str = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    role: str = Field(default="attendee")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
