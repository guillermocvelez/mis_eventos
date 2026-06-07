from uuid import UUID

from app.application.dtos.event_dto import EventUpdateDTO, EventDTO
from app.domain.exceptions import EventNotFound, Unauthorized
from app.domain.ports.event_repository import IEventRepository


class UpdateEventUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, event_id: UUID, dto: EventUpdateDTO, current_user_id: UUID) -> EventDTO:
        event = self.event_repo.find_by_id(event_id)

        if event is None:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        if not event.can_be_edited_by(current_user_id):
            raise Unauthorized()

        updated = event.model_copy(update={
            k: v for k, v in dto.model_dump().items() if v is not None
        })

        saved = self.event_repo.update(updated)

        return EventDTO(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            date=saved.date,
            end_date=saved.end_date,
            location=saved.location,
            capacity=saved.capacity,
            registered_count=saved.registered_count,
            status=saved.status,
            created_by=saved.created_by,
            created_at=saved.created_at,
        )