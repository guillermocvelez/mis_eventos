from uuid import UUID
from typing import Optional
from sqlmodel import Session, select
from app.domain.entities.session_registration import SessionRegistration
from app.domain.entities.session import EventSession
from app.domain.ports.session_registration_repository import ISessionRegistrationRepository
from app.infrastructure.orm.models import SessionRegistrationORM, EventSessionORM


class SQLModelSessionRegistrationRepository(ISessionRegistrationRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, registration: SessionRegistration) -> SessionRegistration:
        orm = SessionRegistrationORM(
            id=registration.id,
            user_id=registration.user_id,
            session_id=registration.session_id,
            registered_at=registration.registered_at,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return registration

    def find_by_user_and_session(self, user_id: UUID, session_id: UUID) -> Optional[SessionRegistration]:
        result = self.db.exec(
            select(SessionRegistrationORM)
            .where(SessionRegistrationORM.user_id == user_id)
            .where(SessionRegistrationORM.session_id == session_id)
        ).first()

        if not result:
            return None

        return SessionRegistration(
            id=result.id,
            user_id=result.user_id,
            session_id=result.session_id,
            registered_at=result.registered_at,
        )

    def find_by_user(self, user_id: UUID) -> list[EventSession]:
        results = self.db.exec(
            select(EventSessionORM)
            .join(SessionRegistrationORM, SessionRegistrationORM.session_id == EventSessionORM.id)
            .where(SessionRegistrationORM.user_id == user_id)
        ).all()

        return [
            EventSession(
                id=r.id,
                event_id=r.event_id,
                title=r.title,
                speaker=r.speaker,
                start_time=r.start_time,
                end_time=r.end_time,
                capacity=r.capacity,
                registered_count=r.registered_count,
            )
            for r in results
        ]

    def delete(self, user_id: UUID, session_id: UUID) -> None:
        result = self.db.exec(
            select(SessionRegistrationORM)
            .where(SessionRegistrationORM.user_id == user_id)
            .where(SessionRegistrationORM.session_id == session_id)
        ).first()

        if result:
            self.db.delete(result)
            self.db.commit()