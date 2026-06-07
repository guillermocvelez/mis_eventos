from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.speaker import Speaker


class ISpeakerRepository(ABC):

    @abstractmethod
    def save(self, speaker: Speaker) -> Speaker:
        ...

    @abstractmethod
    def find_by_id(self, speaker_id: UUID) -> Optional[Speaker]:
        ...

    @abstractmethod
    def find_all(self) -> list[Speaker]:
        ...

    @abstractmethod
    def update(self, speaker: Speaker) -> Speaker:
        ...

    @abstractmethod
    def delete(self, speaker_id: UUID) -> None:
        ...