from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.domain.ports.security import ITokenService
from app.core.config import get_settings

settings = get_settings()

class JWTTokenService(ITokenService):
    def create_token(self, payload: dict) -> str:
        data = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        data["exp"] = expire
        return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except JWTError:
            raise ValueError("Token inválido o expirado")