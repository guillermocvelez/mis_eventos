from typing import Optional
from uuid import UUID
from app.application.dtos.session_dto import SessionDTO
from app.application.dtos.speaker_dto import SpeakerDTO
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.session_repository import ISessionRepository
from app.domain.ports.speaker_repository import ISpeakerRepository
from app.domain.exceptions import EventNotFound


class GetSessionsUseCase:
    def __init__(self, event_repo: IEventRepository, session_repo: ISessionRepository,speaker_repo: ISpeakerRepository):
        self.event_repo = event_repo
        self.session_repo = session_repo
        self.speaker_repo = speaker_repo

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
                speaker=self._resolve_speaker(s.speaker_id),
                start_time=s.start_time,
                end_time=s.end_time,
                capacity=s.capacity,
                registered_count=s.registered_count,
            )
            for s in sessions
        ]
    
    def _resolve_speaker(self, speaker_id) -> Optional[SpeakerDTO]:
        if not speaker_id:
            return None
        speaker = self.speaker_repo.find_by_id(speaker_id)
        if not speaker:
            return None
        return SpeakerDTO(id=speaker.id, name=speaker.name, bio=speaker.bio, email=speaker.email)