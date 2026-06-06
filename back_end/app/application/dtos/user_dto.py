from pydantic import BaseModel

class UserDTO(BaseModel):
    id: int
    email: str
    role: str

class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"