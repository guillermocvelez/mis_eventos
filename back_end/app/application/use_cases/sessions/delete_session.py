from uuid import UUID
from app.domain.ports.session_repository import ISessionRepository
from app.domain.exceptions import EventNotFound


class DeleteSessionUseCase:
    def __init__(self, session_repo: ISessionRepository):
        self.session_repo = session_repo

    def execute(self, session_id: UUID) -> None:
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise EventNotFound(f"Sesión {session_id} no encontrada")

        self.session_repo.delete(session_id)