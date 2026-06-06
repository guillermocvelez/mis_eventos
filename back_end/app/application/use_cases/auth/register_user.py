from app.domain.ports.user_repository import IUserRepository
from app.domain.ports.security import IPasswordHasher, ITokenService
from app.application.dtos.user_dto import TokenDTO
from app.domain.entities.user import User

class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, email: str, password: str) -> TokenDTO:
        existing = self.user_repo.find_by_email(email)
        if existing:
            raise ValueError("El email ya está registrado")

        hashed = self.password_hasher.hash(password)

        user = User(email=email, hashed_password=hashed, role="attendee")
        saved_user = self.user_repo.save(user)

        token = self.token_service.create_token({
            "sub": saved_user.email,
            "role": saved_user.role,
        })
        return TokenDTO(access_token=token)
