from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import SQLModelUserRepository
from app.infrastructure.repositories.event_repository import SQLModelEventRepository
from app.infrastructure.repositories.registration_repository import SQLModelRegistrationRepository
from app.infrastructure.security.password_hasher import BcryptPasswordHasher
from app.infrastructure.security.token_service import JWTTokenService
from app.domain.ports.security import IPasswordHasher, ITokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db_session():
    yield from  get_db()
       

# --- Repositorios ---
def get_user_repo(db: Session = Depends(get_db_session)):
    return SQLModelUserRepository(db)

def get_event_repo(db: Session = Depends(get_db_session)):
    return SQLModelEventRepository(db)

def get_registration_repo(db: Session = Depends(get_db_session)):
    return SQLModelRegistrationRepository(db)

# --- Servicios de seguridad ---
def get_password_hasher() -> IPasswordHasher:
    return BcryptPasswordHasher()

def get_token_service() -> ITokenService:
    return JWTTokenService()

# --- Usuario actual ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo=Depends(get_user_repo),
    token_service: ITokenService = Depends(get_token_service),
):
    try:
        payload = token_service.decode_token(token)
        email = payload.get("sub")
        if not email:
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user = user_repo.find_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    return user

# --- Guard de rol ---
def require_role(*roles: str):
    def checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos")
        return current_user
    return checker