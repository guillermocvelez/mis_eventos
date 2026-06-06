from abc import ABC, abstractmethod


class IPasswordHasher(ABC):

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Recibe contraseña en texto plano, retorna el hash."""
        ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica que la contraseña plana corresponde al hash."""
        ...


class ITokenService(ABC):

    @abstractmethod
    def create_token(self, payload: dict) -> str:
        """Genera un JWT firmado a partir del payload."""
        ...

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decodifica y valida un JWT, retorna el payload."""
        ...