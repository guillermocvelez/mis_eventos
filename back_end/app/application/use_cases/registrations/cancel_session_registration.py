from uuid import UUID

from app.domain.exceptions import EventNotFound, AlreadyRegistered
from app.domain.ports.session_repository import ISessionRepository
from app.domain.ports.session_registration_repository import ISessionRegistrationRepository


class CancelSessionRegistrationUseCase:
    def __init__(
        self,
        session_repo: ISessionRepository,
        session_registration_repo: ISessionRegistrationRepository,
    ):
        self.session_repo = session_repo
        self.session_registration_repo = session_registration_repo

    def execute(self, session_id: UUID, user_id: UUID) -> None:
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise EventNotFound(f"Sesión {session_id} no encontrada")

        registration = self.session_registration_repo.find_by_user_and_session(user_id, session_id)
        if not registration:
            raise AlreadyRegistered("El usuario no está registrado en esta sesión")

        self.session_registration_repo.delete(user_id, session_id)

        updated_session = session.model_copy(update={"registered_count": max(0, session.registered_count - 1)})
        self.session_repo.update(updated_session)