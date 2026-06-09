from uuid import UUID
from typing import Optional
from sqlmodel import Session, select, col, func
from app.domain.entities.event import Event, EventStatus
from app.domain.ports.event_repository import IEventRepository
from app.infrastructure.orm.models import EventORM


class SQLModelEventRepository(IEventRepository):

    def __init__(self, db: Session):
        self.db = db


    def _to_domain(self, orm: EventORM) -> Event:
        return Event(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            date=orm.date,
            end_date=orm.end_date,
            location=orm.location,
            capacity=orm.capacity,
            registered_count=orm.registered_count,
            status=EventStatus(orm.status),
            created_by=orm.created_by,
            created_at=orm.created_at,
        )

    def _to_orm(self, event: Event) -> EventORM:
        return EventORM(
            id=event.id,
            name=event.name,
            description=event.description,
            date=event.date,
            end_date=event.end_date,
            location=event.location,
            capacity=event.capacity,
            registered_count=event.registered_count,
            status=event.status.value,
            created_by=event.created_by,
            created_at=event.created_at,
        )


    def save(self, event: Event) -> Event:
        orm = self._to_orm(event)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        orm = self.db.get(EventORM, event_id)
        if not orm:
            return None
        return self._to_domain(orm)

    def find_all(
        self,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None
    ) -> tuple[list[Event], int]:

        print(f"---------Status enviado: {status}")
        query = select(EventORM)

        if search:
            query = query.where(col(EventORM.name).ilike(f"%{search}%"))

        if status:
            query = query.filter(EventORM.status == status)

        total = len(self.db.exec(query).all())
        query = query.offset((page - 1) * limit).limit(limit)
        results = self.db.exec(query).all()
        return [self._to_domain(r) for r in results], total

    def update(self, event: Event) -> Event:
        orm = self.db.get(EventORM, event.id)
        orm.name = event.name
        orm.description = event.description
        orm.date = event.date
        orm.end_date = event.end_date
        orm.location = event.location
        orm.capacity = event.capacity
        orm.registered_count = event.registered_count
        orm.status = event.status.value
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def delete(self, event_id: UUID) -> None:
        orm = self.db.get(EventORM, event_id)
        self.db.delete(orm)
        self.db.commit()

    def count_by_creator(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(EventORM).where(EventORM.created_by == user_id)
        result = self.db.exec(query).one()
        return int(result)
