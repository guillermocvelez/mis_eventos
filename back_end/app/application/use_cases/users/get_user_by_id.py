from uuid import UUID

from app.application.dtos.user_dto import UserDTO
from app.domain.exceptions import UserNotFound
from app.domain.ports.user_repository import IUserRepository


class GetUserByIdUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: UUID) -> UserDTO:
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise UserNotFound("Usuario no encontrado")

        return UserDTO(
            id=user.id,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )