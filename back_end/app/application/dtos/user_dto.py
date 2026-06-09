from datetime import datetime
from typing import Optional
import uuid

from app.application.dtos.event_dto import EventDTO
from pydantic import BaseModel

class UserDTO(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime

class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreateDTO(BaseModel):
    email: str 
    password: str
    role: Optional[str]
    is_active: bool

class UserUpdateDTO(BaseModel):
    email: Optional[str]
    password: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]

class PaginatedUsersDTO(BaseModel):
    items: list[UserDTO]
    total: int
    page: int
    limit: int
    pages: int



