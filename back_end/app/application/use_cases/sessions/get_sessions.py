from uuid import UUID
from app.application.dtos.session_dto import SessionDTO
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.session_repository import ISessionRepository
from app.domain.exceptions import EventNotFound


class GetSessionsUseCase:
    def __init__(self, event_repo: IEventRepository, session_repo: ISessionRepository):
        self.event_repo = event_repo
        self.session_repo = session_repo

    def execute(self, event_id: UUID) -> list[SessionDTO]:
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        sessions = self.session_repo.find_by_event(event_id)

        return [
            SessionDTO(
                id=s.id,
                event_id=s.event_id,
                title=s.title,
                speaker=s.speaker,
                start_time=s.start_time,
                end_time=s.end_time,
                capacity=s.capacity,
                registered_count=s.registered_count,
            )
            for s in sessions
        ]