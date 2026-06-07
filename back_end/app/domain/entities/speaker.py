import uuid
from typing import Optional
from pydantic import BaseModel


class Speaker(BaseModel):
    id: uuid.UUID
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None