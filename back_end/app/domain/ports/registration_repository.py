from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.registration import Registration
from app.domain.entities.event import Event


class IRegistrationRepository(ABC):

    @abstractmethod
    def save(self, registration: Registration) -> Registration:
        """Persiste un registro nuevo."""
        ...

    @abstractmethod
    def find_by_user_and_event(
        self,
        user_id: UUID,
        event_id: UUID
    ) -> Optional[Registration]:
        """Retorna el registro si existe, None si no."""
        ...

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> list[Event]:
        """Retorna los eventos a los que está registrado el usuario."""
        ...

    @abstractmethod
    def delete(self, user_id: UUID, event_id: UUID) -> None:
        """Elimina el registro de un usuario a un evento."""
        ...