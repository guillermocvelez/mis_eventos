from app.domain.ports.user_repository import IUserRepository
from app.domain.ports.security import IPasswordHasher, ITokenService
from app.application.dtos.user_dto import TokenDTO

class LoginUserUseCase:
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
        # 1. Buscar el usuario
        user = self.user_repo.find_by_email(email)
        if not user:
            raise ValueError("Credenciales inválidas")

        # 2. Verificar la contraseña
        if not self.password_hasher.verify(password, user.hashed_password):
            raise ValueError("Credenciales inválidas")

        # 3. Generar y retornar el token
        token = self.token_service.create_token({
            "sub": user.email,
            "role": user.role,
        })
        return TokenDTO(access_token=token)
