from uuid import UUID
from typing import Optional
from sqlmodel import Session, select
from app.domain.entities.session import EventSession
from app.domain.ports.session_repository import ISessionRepository
from app.infrastructure.orm.models import EventSessionORM


class SQLModelSessionRepository(ISessionRepository):

    def __init__(self, db: Session):
        self.db = db


    def _to_domain(self, orm: EventSessionORM) -> EventSession:
        return EventSession(
            id=orm.id,
            event_id=orm.event_id,
            title=orm.title,
            speaker_id=orm.speaker_id,
            start_time=orm.start_time,
            end_time=orm.end_time,
            capacity=orm.capacity,
            registered_count=orm.registered_count,
        )

    def _to_orm(self, session: EventSession) -> EventSessionORM:
        return EventSessionORM(
            id=session.id,
            event_id=session.event_id,
            title=session.title,
            speaker_id=session.speaker_id,
            start_time=session.start_time,
            end_time=session.end_time,
            capacity=session.capacity,
            registered_count=session.registered_count,
        )


    def save(self, session: EventSession) -> EventSession:
        orm = self._to_orm(session)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def find_by_event(self, event_id: UUID) -> list[EventSession]:
        query = select(EventSessionORM).where(EventSessionORM.event_id == event_id)
        results = self.db.exec(query).all()
        return [self._to_domain(r) for r in results]

    def find_by_id(self, session_id: UUID) -> Optional[EventSession]:
        orm = self.db.get(EventSessionORM, session_id)
        if not orm:
            return None
        return self._to_domain(orm)

    def update(self, session: EventSession) -> EventSession:
        orm = self.db.get(EventSessionORM, session.id)
        orm.title = session.title
        orm.speaker_id = session.speaker_id
        orm.start_time = session.start_time
        orm.end_time = session.end_time
        orm.capacity = session.capacity
        orm.registered_count = session.registered_count
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def delete(self, session_id: UUID) -> None:
        orm = self.db.get(EventSessionORM, session_id)
        self.db.delete(orm)
        self.db.commit()