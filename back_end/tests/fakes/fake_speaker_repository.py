from uuid import UUID
from typing import Optional

from app.domain.entities.speaker import Speaker
from app.domain.ports.speaker_repository import ISpeakerRepository


class FakeSpeakerRepository(ISpeakerRepository):
    def __init__(self):
        self._speakers: list[Speaker] = []

    def save(self, speaker: Speaker) -> Speaker:
        self._speakers.append(speaker)
        return speaker

    def find_by_id(self, speaker_id: UUID) -> Optional[Speaker]:
        return next((s for s in self._speakers if s.id == speaker_id), None)

    def find_all(self) -> list[Speaker]:
        return list(self._speakers)

    def update(self, speaker: Speaker) -> Speaker:
        self._speakers = [speaker if s.id == speaker.id else s for s in self._speakers]
        return speaker

    def delete(self, speaker_id: UUID) -> None:
        self._speakers = [s for s in self._speakers if s.id != speaker_id]
