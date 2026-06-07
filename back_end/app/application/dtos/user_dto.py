import uuid

from pydantic import BaseModel

class UserDTO(BaseModel):
    id: uuid.UUID
    email: str
    role: str

class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
