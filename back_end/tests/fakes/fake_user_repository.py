from __future__ import annotations

from app.domain.ports.user_repository import IUserRepository
from app.domain.entities.user import User

class FakeUserRepository(IUserRepository):
    def __init__(self):
        self._users: list[User] = []

    def save(self, user: User) -> User:
        self._users.append(user)
        return user

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email), None)

    def find_by_id(self, user_id: int) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)
