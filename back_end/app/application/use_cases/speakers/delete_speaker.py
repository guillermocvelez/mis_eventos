from uuid import UUID
from app.domain.exceptions import EventNotFound
from app.domain.ports.speaker_repository import ISpeakerRepository


class DeleteSpeakerUseCase:
    def __init__(self, speaker_repo: ISpeakerRepository):
        self.speaker_repo = speaker_repo

    def execute(self, speaker_id: UUID) -> None:
        speaker = self.speaker_repo.find_by_id(speaker_id)
        if not speaker:
            raise EventNotFound(f"Ponente {speaker_id} no encontrado")
        self.speaker_repo.delete(speaker_id)