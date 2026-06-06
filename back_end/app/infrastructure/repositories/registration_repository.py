from uuid import UUID
from typing import Optional
from sqlmodel import Session, select
from app.domain.entities.registration import Registration
from app.domain.entities.event import Event, EventStatus
from app.domain.ports.registration_repository import IRegistrationRepository
from app.infrastructure.orm.models import RegistrationORM, EventORM


class SQLModelRegistrationRepository(IRegistrationRepository):

    def __init__(self, db: Session):
        self.db = db


    def _to_domain(self, orm: RegistrationORM) -> Registration:
        return Registration(
            id=orm.id,
            user_id=orm.user_id,
            event_id=orm.event_id,
            registered_at=orm.registered_at,
        )

    def _event_orm_to_domain(self, orm: EventORM) -> Event:
        return Event(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            date=orm.date,
            location=orm.location,
            capacity=orm.capacity,
            registered_count=orm.registered_count,
            status=EventStatus(orm.status),
            created_by=orm.created_by,
            created_at=orm.created_at,
        )


    def save(self, registration: Registration) -> Registration:
        orm = RegistrationORM(
            id=registration.id,
            user_id=registration.user_id,
            event_id=registration.event_id,
            registered_at=registration.registered_at,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def find_by_user_and_event(
        self,
        user_id: UUID,
        event_id: UUID
    ) -> Optional[Registration]:
        query = select(RegistrationORM).where(
            RegistrationORM.user_id == user_id,
            RegistrationORM.event_id == event_id,
        )
        orm = self.db.exec(query).first()
        if not orm:
            return None
        return self._to_domain(orm)

    def find_by_user(self, user_id: UUID) -> list[Event]:
        query = (
            select(EventORM)
            .join(RegistrationORM, RegistrationORM.event_id == EventORM.id)
            .where(RegistrationORM.user_id == user_id)
        )
        results = self.db.exec(query).all()
        return [self._event_orm_to_domain(r) for r in results]

    def delete(self, user_id: UUID, event_id: UUID) -> None:
        query = select(RegistrationORM).where(
            RegistrationORM.user_id == user_id,
            RegistrationORM.event_id == event_id,
        )
        orm = self.db.exec(query).first()
        self.db.delete(orm)
        self.db.commit()