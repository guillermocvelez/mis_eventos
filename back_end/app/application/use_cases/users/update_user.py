from uuid import UUID

from app.application.dtos.user_dto import UserDTO, UserUpdateDTO
from app.domain.exceptions import EmailAlreadyExists, UserNotFound
from app.domain.ports.security import IPasswordHasher
from app.domain.ports.user_repository import IUserRepository


class UpdateUserUseCase:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    def execute(self, user_id: UUID, dto: UserUpdateDTO) -> UserDTO:
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise UserNotFound("Usuario no encontrado")

        if dto.email and dto.email != user.email:
            existing_user = self.user_repo.find_by_email(dto.email)

            if existing_user:
                raise EmailAlreadyExists(dto.email)

            user.email = dto.email

        if dto.password:
            user.hashed_password = self.password_hasher.hash(dto.password)

        if dto.role is not None:
            user.role = dto.role

        if dto.is_active is not None:
            user.is_active = dto.is_active

        updated_user = self.user_repo.update(user)

        return UserDTO(
            id=updated_user.id,
            email=updated_user.email,
            role=updated_user.role.value,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
        )