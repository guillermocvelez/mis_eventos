from app.application.dtos.speaker_dto import SpeakerDTO
from app.domain.ports.speaker_repository import ISpeakerRepository


class GetSpeakersUseCase:
    def __init__(self, speaker_repo: ISpeakerRepository):
        self.speaker_repo = speaker_repo

    def execute(self) -> list[SpeakerDTO]:
        speakers = self.speaker_repo.find_all()
        return [SpeakerDTO(id=s.id, name=s.name, bio=s.bio, email=s.email) for s in speakers]
    