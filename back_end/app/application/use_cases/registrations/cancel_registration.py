from uuid import UUID

from app.domain.exceptions import EventNotFound, AlreadyRegistered, RegistrationNotFound
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.registration_repository import IRegistrationRepository


class CancelRegistrationUseCase:
    def __init__(self, event_repo: IEventRepository, registration_repo: IRegistrationRepository):
        self.event_repo = event_repo
        self.registration_repo = registration_repo

    def execute(self, event_id: UUID, user_id: UUID) -> None:
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        registration = self.registration_repo.find_by_user_and_event(user_id, event_id)
        if not registration:
            raise RegistrationNotFound("El usuario no está registrado en este evento")

        self.registration_repo.delete(user_id, event_id)

        updated_event = event.model_copy(update={"registered_count": max(0, event.registered_count - 1)})
        self.event_repo.update(updated_event)