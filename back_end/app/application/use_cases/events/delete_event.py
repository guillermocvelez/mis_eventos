from uuid import UUID

from app.domain.exceptions import EventNotFound, Unauthorized
from app.domain.ports.event_repository import IEventRepository


class DeleteEventUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, event_id: UUID, current_user_id: UUID) -> None:
        event = self.event_repo.find_by_id(event_id)

        if event is None:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        if not event.can_be_edited_by(current_user_id):
            raise Unauthorized()

        self.event_repo.delete(event_id)
