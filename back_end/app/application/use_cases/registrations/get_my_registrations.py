from uuid import UUID

from app.application.dtos.event_dto import EventDTO
from app.domain.ports.registration_repository import IRegistrationRepository


class GetMyRegistrationsUseCase:
    def __init__(self, registration_repo: IRegistrationRepository):
        self.registration_repo = registration_repo

    def execute(self, user_id: UUID) -> list[EventDTO]:
        events = self.registration_repo.find_by_user(user_id)

        return [
            EventDTO(
                id=e.id,
                name=e.name,
                description=e.description,
                date=e.date,
                end_date=e.end_date,
                location=e.location,
                capacity=e.capacity,
                registered_count=e.registered_count,
                status=e.status,
                created_by=e.created_by,
                created_at=e.created_at,
            )
            for e in events
        ]