from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.user import User


class IUserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        """Persiste un usuario nuevo."""
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Retorna el usuario si existe, None si no."""
        ...

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Retorna el usuario si existe, None si no."""
        ...