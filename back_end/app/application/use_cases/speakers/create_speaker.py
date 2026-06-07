from uuid import uuid4
from app.application.dtos.speaker_dto import SpeakerCreateDTO, SpeakerDTO
from app.domain.entities.speaker import Speaker
from app.domain.ports.speaker_repository import ISpeakerRepository


class CreateSpeakerUseCase:
    def __init__(self, speaker_repo: ISpeakerRepository):
        self.speaker_repo = speaker_repo

    def execute(self, dto: SpeakerCreateDTO) -> SpeakerDTO:
        speaker = Speaker(id=uuid4(), name=dto.name, bio=dto.bio, email=dto.email)
        saved = self.speaker_repo.save(speaker)
        return SpeakerDTO(id=saved.id, name=saved.name, bio=saved.bio, email=saved.email)