from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.event import Event


class IEventRepository(ABC):

    @abstractmethod
    def save(self, event: Event) -> Event:
        """Persiste un evento nuevo y lo retorna con su id asignado."""
        ...

    @abstractmethod
    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        """Retorna el evento si existe, None si no."""
        ...

    @abstractmethod
    def find_all(
        self,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> tuple[list[Event], int]:
        """Retorna la lista paginada y el total de resultados."""
        ...

    @abstractmethod
    def update(self, event: Event) -> Event:
        """Actualiza un evento existente."""
        ...

    @abstractmethod
    def delete(self, event_id: UUID) -> None:
        """Elimina un evento por id."""
        ...