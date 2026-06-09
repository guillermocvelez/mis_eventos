from uuid import UUID

from app.domain.exceptions import CannotDeleteSelf, UserNotFound
from app.domain.ports.user_repository import IUserRepository


class DeleteUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: UUID, current_user_id: UUID) -> None:
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise UserNotFound("Usuario no encontrado")

        if user.id == current_user_id:
            raise CannotDeleteSelf()

        self.user_repo.delete(user_id)