from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.dtos.user_dto import TokenDTO, UserDTO
from app.infrastructure.web.dependencies import (
    get_user_repo,
    get_password_hasher,
    get_token_service,
    get_current_user,
)
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=TokenDTO)
def register(
    body: RegisterRequest,
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    token_service=Depends(get_token_service),
):
    try:
        use_case = RegisterUserUseCase(user_repo, password_hasher, token_service)
        return use_case.execute(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenDTO)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    token_service=Depends(get_token_service),
):
    try:
        use_case = LoginUserUseCase(user_repo, password_hasher, token_service)
        return use_case.execute(form.username, form.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


