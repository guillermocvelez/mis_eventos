from uuid import UUID
from typing import Optional
from sqlmodel import Session, select, col, or_
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
            name=orm.name,
            hashed_password=orm.hashed_password,
            role=UserRole(orm.role),
            is_active=orm.is_active,
            created_at=orm.created_at,
        )

    def _to_orm(self, user: User) -> UserORM:
        return UserORM(
            id=user.id,
            email=user.email,
            name=user.name,
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

    def find_by_name(self, name: str) -> Optional[User]:
        query = select(UserORM).where(col(UserORM.name).ilike(f"{name}"))  
        orm = self.db.exec(query).all()
        if not orm:
            return None
        return self._to_domain(orm)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        orm = self.db.get(UserORM, user_id)
        if not orm:
            return None
        return self._to_domain(orm)

    def find_all(
        self,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[User], int]:
        query = select(UserORM)

        if search:
            query = query = query.where(
            or_(
                col(UserORM.email).ilike(f"%{search}%"),
                col(UserORM.name).ilike(f"%{search}%")
            )
    )

        if role:
            query = query.where(UserORM.role == role.value)

        if is_active is not None:
            query = query.where(UserORM.is_active == is_active)

        total = len(self.db.exec(query).all())

        query = query.offset((page - 1) * limit).limit(limit)
        results = self.db.exec(query).all()

        return [self._to_domain(user) for user in results], total

    def update(self, user: User) -> User:
        orm = self.db.get(UserORM, user.id)

        orm.email = user.email
        orm.name = user.name
        orm.hashed_password = user.hashed_password
        orm.role = user.role.value
        orm.is_active = user.is_active

        self.db.commit()
        self.db.refresh(orm)

        return self._to_domain(orm)

    def delete(self, user_id: UUID) -> None:
        orm = self.db.get(UserORM, user_id)

        orm.is_active = False