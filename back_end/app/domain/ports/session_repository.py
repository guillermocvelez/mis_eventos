from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.session import EventSession


class ISessionRepository(ABC):

    @abstractmethod
    def save(self, session: EventSession) -> EventSession:
        """Persiste una sesión nueva."""
        ...

    @abstractmethod
    def find_by_event(self, event_id: UUID) -> list[EventSession]:
        """Retorna todas las sesiones de un evento."""
        ...

    @abstractmethod
    def find_by_id(self, session_id: UUID) -> Optional[EventSession]:
        """Retorna la sesión si existe, None si no."""
        ...

    @abstractmethod
    def update(self, session: EventSession) -> EventSession:
        """Actualiza una sesión existente."""
        ...

    @abstractmethod
    def delete(self, session_id: UUID) -> None:
        """Elimina una sesión por id."""
        ...