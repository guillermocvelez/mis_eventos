from abc import ABC, abstractmethod

class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain: str) -> str: ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...

class ITokenService(ABC):
    @abstractmethod
    def create_token(self, payload: dict) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> dict: ...