from uuid import UUID
from typing import Optional
from types import SimpleNamespace

from app.domain.entities.session import EventSession
from app.domain.entities.session_registration import SessionRegistration
from app.domain.ports.session_registration_repository import (
    ISessionRegistrationRepository,
)


class FakeSessionRegistrationRepository(ISessionRegistrationRepository):
    def __init__(self):
        self._registrations: list[SessionRegistration] = []
        self._sessions: dict[UUID, EventSession] = {}

    def add_session(self, session: EventSession) -> None:
        self._sessions[session.id] = session

    def save(self, registration: SessionRegistration) -> SessionRegistration:
        self._registrations.append(registration)
        return registration

    def find_by_user_and_session(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> Optional[SessionRegistration]:
        return next(
            (
                r
                for r in self._registrations
                if r.user_id == user_id and r.session_id == session_id
            ),
            None,
        )

    def find_by_user(self, user_id: UUID) -> list[EventSession]:
        return [
            SimpleNamespace(
                id=session.id,
                event_id=session.event_id,
                title=session.title,
                speaker_id=session.speaker_id,
                start_time=session.start_time,
                end_time=session.end_time,
                capacity=session.capacity,
                registered_count=session.registered_count,
            )
            for r in self._registrations
            if r.user_id == user_id and r.session_id in self._sessions
            for session in [self._sessions[r.session_id]]
        ]

    def delete(self, user_id: UUID, session_id: UUID) -> None:
        self._registrations = [
            r
            for r in self._registrations
            if not (r.user_id == user_id and r.session_id == session_id)
        ]
