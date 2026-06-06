from passlib.context import CryptContext
from app.domain.ports.security import IPasswordHasher

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptPasswordHasher(IPasswordHasher):
    def hash(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)