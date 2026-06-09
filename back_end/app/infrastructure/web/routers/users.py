from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dtos.user_dto import (
    PaginatedUsersDTO,
    UserCreateDTO,
    UserDTO,
    UserUpdateDTO,
)
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.application.use_cases.users.delete_user import DeleteUserUseCase
from app.application.use_cases.users.get_user_by_id import GetUserByIdUseCase
from app.application.use_cases.users.get_users import GetUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
from app.domain.entities.user import UserRole
from app.domain.exceptions import CannotDeleteSelf, EmailAlreadyExists, UserNotFound
from app.infrastructure.web.dependencies import (
    get_password_hasher,
    get_user_repo,
    require_role,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=PaginatedUsersDTO)
def get_users(
    search: str | None = Query(default=None),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    user_repo=Depends(get_user_repo),
    _=Depends(require_role("admin")),
):
    return GetUsersUseCase(user_repo).execute(
        search=search,
        role=role,
        is_active=is_active,
        page=page,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserDTO)
def get_user_by_id(
    user_id: UUID,
    user_repo=Depends(get_user_repo),
    _=Depends(require_role("admin")),
):
    try:
        return GetUserByIdUseCase(user_repo).execute(user_id)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    dto: UserCreateDTO,
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    _=Depends(require_role("admin")),
):
    try:
        return CreateUserUseCase(user_repo, password_hasher).execute(dto)
    except EmailAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{user_id}", response_model=UserDTO)
def update_user(
    user_id: UUID,
    dto: UserUpdateDTO,
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    _=Depends(require_role("admin")),
):
    try:
        return UpdateUserUseCase(user_repo, password_hasher).execute(user_id, dto)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    user_repo=Depends(get_user_repo),
    current_user=Depends(require_role("admin")),
):
    try:
        DeleteUserUseCase(user_repo).execute(user_id, current_user.id)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CannotDeleteSelf as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))