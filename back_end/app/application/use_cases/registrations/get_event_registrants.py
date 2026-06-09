from uuid import UUID

from app.application.dtos.registration_dto import EventRegistrantDTO
from app.domain.exceptions import EventNotFound
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.registration_repository import IRegistrationRepository


class GetEventRegistrantsUseCase:
    def __init__(
        self,
        event_repo: IEventRepository,
        registration_repo: IRegistrationRepository,
    ):
        self.event_repo = event_repo
        self.registration_repo = registration_repo

    def execute(self, event_id: UUID) -> list[EventRegistrantDTO]:
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        return self.registration_repo.find_users_by_event(event_id)
