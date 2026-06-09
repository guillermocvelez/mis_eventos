from app.application.dtos.user_dto import UserCreateDTO, UserDTO
from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyExists
from app.domain.ports.security import IPasswordHasher
from app.domain.ports.user_repository import IUserRepository


class CreateUserUseCase:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    def execute(self, dto: UserCreateDTO) -> UserDTO:
        existing_user = self.user_repo.find_by_email(dto.email)

        if existing_user:
            raise EmailAlreadyExists(dto.email)

        user = User(
            email=dto.email,
            name=dto.name,
            hashed_password=self.password_hasher.hash(dto.password),
            role=dto.role,
            is_active=dto.is_active,
        )

        saved_user = self.user_repo.save(user)

        return UserDTO(
            id=saved_user.id,
            email=saved_user.email,
            name=saved_user.name,
            role=saved_user.role.value,
            is_active=saved_user.is_active,
            created_at=saved_user.created_at,
        )