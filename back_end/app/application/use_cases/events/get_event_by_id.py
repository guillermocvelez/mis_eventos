from uuid import UUID

from app.application.dtos.event_dto import EventDTO
from app.domain.exceptions import EventNotFound
from app.domain.ports.event_repository import IEventRepository


class GetEventByIdUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, event_id: UUID) -> EventDTO:
        event = self.event_repo.find_by_id(event_id)

        if event is None:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        return EventDTO(
            id=event.id,
            name=event.name,
            description=event.description,
            date=event.date,
            location=event.location,
            capacity=event.capacity,
            registered_count=event.registered_count,
            status=event.status,
            created_by=event.created_by,
            created_at=event.created_at,
        )