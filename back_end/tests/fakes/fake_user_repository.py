from __future__ import annotations

from uuid import UUID
from typing import Optional

from app.domain.ports.user_repository import IUserRepository
from app.domain.entities.user import User, UserRole

class FakeUserRepository(IUserRepository):
    def __init__(self):
        self._users: list[User] = []

    def save(self, user: User) -> User:
        self._users.append(user)
        return user

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email), None)

    def find_by_id(self, user_id: UUID) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def find_by_name(self, name: str) -> User | None:
        return next((u for u in self._users if u.name == name), None)

    def find_all(
        self,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[User], int]:
        results = self._users

        if search:
            normalized_search = search.lower()
            results = [
                u
                for u in results
                if normalized_search in u.name.lower()
                or normalized_search in u.email.lower()
            ]

        if role is not None:
            results = [u for u in results if u.role == role]

        if is_active is not None:
            results = [u for u in results if u.is_active == is_active]

        total = len(results)
        start = (page - 1) * limit
        end = start + limit

        return results[start:end], total

    def update(self, user: User) -> User:
        self._users = [user if u.id == user.id else u for u in self._users]
        return user

    def delete(self, user_id: UUID) -> None:
        self._users = [u for u in self._users if u.id != user_id]
