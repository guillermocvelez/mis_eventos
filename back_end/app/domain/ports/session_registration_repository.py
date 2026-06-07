from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.session_registration import SessionRegistration
from app.domain.entities.session import EventSession


class ISessionRegistrationRepository(ABC):

    @abstractmethod
    def save(self, registration: SessionRegistration) -> SessionRegistration:
        """Persiste un registro a sesión."""
        ...

    @abstractmethod
    def find_by_user_and_session(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> Optional[SessionRegistration]:
        """Retorna el registro si existe, None si no."""
        ...

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> list[EventSession]:
        """Retorna las sesiones a las que está registrado el usuario."""
        ...

    @abstractmethod
    def delete(self, user_id: UUID, session_id: UUID) -> None:
        """Elimina el registro de un usuario a una sesión."""
        ...