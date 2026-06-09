import math
from typing import Optional

from app.application.dtos.user_dto import PaginatedUsersDTO, UserDTO
from app.domain.entities.user import UserRole
from app.domain.ports.user_repository import IUserRepository


class GetUsersUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def execute(
        self,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 10,
    ) -> PaginatedUsersDTO:
        users, total = self.user_repo.find_all(
            search=search,
            role=role,
            is_active=is_active,
            page=page,
            limit=limit,
        )

        return PaginatedUsersDTO(
            items=[
                UserDTO(
                    id=user.id,
                    email=user.email,
                    role=user.role.value,
                    is_active=user.is_active,
                    created_at=user.created_at,
                )
                for user in users
            ],
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if total > 0 else 1,
        )

