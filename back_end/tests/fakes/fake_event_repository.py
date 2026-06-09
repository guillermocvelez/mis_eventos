from uuid import UUID
from typing import Optional
from app.domain.ports.event_repository import IEventRepository
from app.domain.entities.event import Event


class FakeEventRepository(IEventRepository):
    def __init__(self):
        self._events: list[Event] = []

    def save(self, event: Event) -> Event:
        self._events.append(event)
        return event

    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        return next((e for e in self._events if e.id == event_id), None)

    def find_all(
        self,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> tuple[list[Event], int]:
        results = self._events

        if search:
            results = [e for e in results if search.lower() in e.name.lower()]

        if status:
            results = [e for e in results if e.status == status]

        total = len(results)
        start = (page - 1) * limit
        end = start + limit

        return results[start:end], total

    def update(self, event: Event) -> Event:
        self._events = [event if e.id == event.id else e for e in self._events]
        return event

    def delete(self, event_id: UUID) -> None:
        self._events = [e for e in self._events if e.id != event_id]

    def count_by_creator(self, user_id: UUID) -> int:
        return len([e for e in self._events if e.created_by == user_id])
