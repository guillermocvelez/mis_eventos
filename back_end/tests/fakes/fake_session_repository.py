from uuid import UUID
from typing import Optional
from app.domain.ports.session_repository import ISessionRepository
from app.domain.entities.session import EventSession


class FakeSessionRepository(ISessionRepository):
    def __init__(self):
        self._sessions: list[EventSession] = []

    def save(self, session: EventSession) -> EventSession:
        self._sessions.append(session)
        return session

    def find_by_event(self, event_id: UUID) -> list[EventSession]:
        return [s for s in self._sessions if s.event_id == event_id]

    def find_by_id(self, session_id: UUID) -> Optional[EventSession]:
        return next((s for s in self._sessions if s.id == session_id), None)

    def update(self, session: EventSession) -> EventSession:
        self._sessions = [session if s.id == session.id else s for s in self._sessions]
        return session

    def delete(self, session_id: UUID) -> None:
        self._sessions = [s for s in self._sessions if s.id != session_id]