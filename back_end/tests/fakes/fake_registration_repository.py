from uuid import UUID
from typing import Optional

from app.domain.entities.event import Event
from app.domain.entities.registration import Registration
from app.domain.ports.registration_repository import IRegistrationRepository


class FakeRegistrationRepository(IRegistrationRepository):
    def __init__(self):
        self._registrations: list[Registration] = []
        self._events: dict[UUID, Event] = {}

    def add_event(self, event: Event) -> None:
        self._events[event.id] = event

    def save(self, registration: Registration) -> Registration:
        self._registrations.append(registration)
        return registration

    def find_by_user_and_event(
        self,
        user_id: UUID,
        event_id: UUID,
    ) -> Optional[Registration]:
        return next(
            (
                r
                for r in self._registrations
                if r.user_id == user_id and r.event_id == event_id
            ),
            None,
        )

    def find_by_user(self, user_id: UUID) -> list[Event]:
        return [
            self._events[r.event_id]
            for r in self._registrations
            if r.user_id == user_id and r.event_id in self._events
        ]

    def delete(self, user_id: UUID, event_id: UUID) -> None:
        self._registrations = [
            r
            for r in self._registrations
            if not (r.user_id == user_id and r.event_id == event_id)
        ]
