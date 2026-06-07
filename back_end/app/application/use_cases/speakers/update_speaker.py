from uuid import UUID
from app.application.dtos.speaker_dto import SpeakerUpdateDTO, SpeakerDTO
from app.domain.exceptions import EventNotFound
from app.domain.ports.speaker_repository import ISpeakerRepository


class UpdateSpeakerUseCase:
    def __init__(self, speaker_repo: ISpeakerRepository):
        self.speaker_repo = speaker_repo

    def execute(self, speaker_id: UUID, dto: SpeakerUpdateDTO) -> SpeakerDTO:
        speaker = self.speaker_repo.find_by_id(speaker_id)
        if not speaker:
            raise EventNotFound(f"Ponente {speaker_id} no encontrado")

        updated = speaker.model_copy(update={
            k: v for k, v in dto.model_dump().items() if v is not None
        })
        saved = self.speaker_repo.update(updated)
        return SpeakerDTO(id=saved.id, name=saved.name, bio=saved.bio, email=saved.email)