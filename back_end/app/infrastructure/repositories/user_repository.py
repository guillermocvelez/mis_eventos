from uuid import UUID
from typing import Optional
from sqlmodel import Session, select
from app.domain.entities.user import User, UserRole
from app.domain.ports.user_repository import IUserRepository
from app.infrastructure.orm.models import UserORM


class SQLModelUserRepository(IUserRepository):

    def __init__(self, db: Session):
        self.db = db


    def _to_domain(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=orm.email,
            hashed_password=orm.hashed_password,
            role=UserRole(orm.role),
            is_active=orm.is_active,
            created_at=orm.created_at,
        )

    def _to_orm(self, user: User) -> UserORM:
        return UserORM(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )


    def save(self, user: User) -> User:
        orm = self._to_orm(user)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def find_by_email(self, email: str) -> Optional[User]:
        query = select(UserORM).where(UserORM.email == email)
        orm = self.db.exec(query).first()
        if not orm:
            return None
        return self._to_domain(orm)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        orm = self.db.get(UserORM, user_id)
        if not orm:
            return None
        return self._to_domain(orm)
