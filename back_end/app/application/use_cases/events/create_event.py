from datetime import datetime, timezone
import uuid

from app.application.dtos.event_dto import EventCreateDTO, EventDTO
from app.domain.entities.event import Event, EventStatus
from app.domain.exceptions import InvalidEventDate
from app.domain.ports.event_repository import IEventRepository


class CreateEventUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, dto: EventCreateDTO, organizer_id: uuid.UUID) -> EventDTO:
        if dto.date <= datetime.now(timezone.utc):
            raise InvalidEventDate("La fecha del evento debe ser futura")

        event = Event(
            id=uuid.uuid4(),
            name=dto.name,
            description=dto.description,
            date=dto.date,
            end_date=dto.end_date,
            location=dto.location,
            capacity=dto.capacity,
            created_by=organizer_id,
            created_at=datetime.now(timezone.utc),
            status=EventStatus.draft,
        )

        saved = self.event_repo.save(event)

        return EventDTO(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            date=saved.date,
            end_date=dto.end_date,
            location=saved.location,
            capacity=saved.capacity,
            registered_count=saved.registered_count,
            status=saved.status,
            created_by=saved.created_by,
            created_at=saved.created_at,
        )