from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.domain.entities.registration import Registration
from app.domain.exceptions import CapacityExceeded, AlreadyRegistered, EventNotFound
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.registration_repository import IRegistrationRepository


class RegisterToEventUseCase:
    def __init__(self, event_repo: IEventRepository, registration_repo: IRegistrationRepository):
        self.event_repo = event_repo
        self.registration_repo = registration_repo

    def execute(self, event_id: UUID, user_id: UUID) -> Registration:
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        if not event.has_capacity():
            raise CapacityExceeded("El evento no tiene capacidad disponible")

        existing = self.registration_repo.find_by_user_and_event(user_id, event_id)
        if existing:
            raise AlreadyRegistered("El usuario ya está registrado en este evento")

        registration = Registration(
            id=uuid4(),
            user_id=user_id,
            event_id=event_id,
            registered_at=datetime.now(timezone.utc),
        )

        self.registration_repo.save(registration)

        updated_event = event.model_copy(update={"registered_count": event.registered_count + 1})
        self.event_repo.update(updated_event)

        return registration