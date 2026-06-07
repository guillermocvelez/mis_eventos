from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class SpeakerCreateDTO(BaseModel):
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None


class SpeakerUpdateDTO(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None


class SpeakerDTO(BaseModel):
    id: UUID
    name: str
    bio: Optional[str] = None
    email: Optional[str] = None