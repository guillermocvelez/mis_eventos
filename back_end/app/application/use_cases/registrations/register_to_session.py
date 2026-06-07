from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.domain.entities.session_registration import SessionRegistration
from app.domain.exceptions import EventNotFound, CapacityExceeded, AlreadyRegistered
from app.domain.ports.registration_repository import IRegistrationRepository
from app.domain.ports.session_repository import ISessionRepository
from app.domain.ports.session_registration_repository import ISessionRegistrationRepository


class RegisterToSessionUseCase:
    def __init__(
        self,
        registration_repo: IRegistrationRepository,
        session_repo: ISessionRepository,
        session_registration_repo: ISessionRegistrationRepository,
    ):
        self.registration_repo = registration_repo
        self.session_repo = session_repo
        self.session_registration_repo = session_registration_repo

    def execute(self, session_id: UUID, user_id: UUID) -> SessionRegistration:
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise EventNotFound(f"Sesión {session_id} no encontrada")

        existing_event_reg = self.registration_repo.find_by_user_and_event(user_id, session.event_id)
        if not existing_event_reg:
            raise AlreadyRegistered("Debes registrarte al evento antes de registrarte a una sesión")

        if session.capacity is not None and session.registered_count >= session.capacity:
            raise CapacityExceeded("La sesión no tiene capacidad disponible")

        existing = self.session_registration_repo.find_by_user_and_session(user_id, session_id)
        if existing:
            raise AlreadyRegistered("El usuario ya está registrado en esta sesión")

        registration = SessionRegistration(
            id=uuid4(),
            user_id=user_id,
            session_id=session_id,
            registered_at=datetime.now(timezone.utc),
        )

        self.session_registration_repo.save(registration)

        updated_session = session.model_copy(update={"registered_count": session.registered_count + 1})
        self.session_repo.update(updated_session)

        return registration