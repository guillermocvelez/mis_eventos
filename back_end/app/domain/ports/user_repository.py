from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.user import User, UserRole


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

    @abstractmethod
    def find_all(
        self,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[User], int]:
        """Retorna usuarios paginados y el total de resultados."""
        ...

    @abstractmethod
    def update(self, user: User) -> User:
        """Actualiza un usuario existente."""
        ...

    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        """Desactiva o elimina un usuario."""
        ...
    