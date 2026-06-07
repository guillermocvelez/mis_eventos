from uuid import UUID

from app.application.dtos.session_dto import SessionDTO
from app.domain.ports.session_registration_repository import ISessionRegistrationRepository


class GetMySessionRegistrationsUseCase:
    def __init__(self, session_registration_repo: ISessionRegistrationRepository):
        self.session_registration_repo = session_registration_repo

    def execute(self, user_id: UUID) -> list[SessionDTO]:
        sessions = self.session_registration_repo.find_by_user(user_id)

        return [
            SessionDTO(
                id=s.id,
                event_id=s.event_id,
                title=s.title,
                speaker=s.speaker,
                start_time=s.start_time,
                end_time=s.end_time,
                capacity=s.capacity,
                registered_count=s.registered_count,
            )
            for s in sessions
        ]