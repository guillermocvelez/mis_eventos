from app.domain.ports.user_repository import IUserRepository
from app.domain.ports.security import IPasswordHasher
from app.application.dtos.user_dto import UserDTO
from app.domain.entities.user import User
from app.domain.exceptions import AlreadyRegistered

class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher = None,
        hasher: IPasswordHasher = None,
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher or hasher

    def execute(self, email: str, name: str, password: str) -> UserDTO:
        existing = self.user_repo.find_by_email(email)
        if existing:
            raise AlreadyRegistered()

        hashed = self.password_hasher.hash(password)

        user = User(email=email, name=name, hashed_password=hashed, role="attendee")
        saved_user = self.user_repo.save(user)

        return UserDTO(
            id=saved_user.id,
            email=saved_user.email,
            name=saved_user.name,
            role=saved_user.role.value,
            is_active=saved_user.is_active,
            created_at=saved_user.created_at,
        )
