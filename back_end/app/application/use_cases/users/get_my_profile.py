from app.application.dtos.user_profile_dto import UserProfileDTO
from app.domain.entities.user import User
from app.domain.exceptions import UserNotFound
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.registration_repository import IRegistrationRepository
from app.domain.ports.user_repository import IUserRepository


class GetMyProfileUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        event_repo: IEventRepository,
        registration_repo: IRegistrationRepository,
    ):
        self.user_repo = user_repo
        self.event_repo = event_repo
        self.registration_repo = registration_repo

    def execute(self, current_user: User) -> UserProfileDTO:
        user = self.user_repo.find_by_id(current_user.id)
        if not user:
            raise UserNotFound("Usuario no encontrado")

        registered_count = len(self.registration_repo.find_by_user(user.id))
        organized_count = self.event_repo.count_by_creator(user.id)

        return UserProfileDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
            is_active=user.is_active,
            organized_count=organized_count,
            registered_count=registered_count,
        )