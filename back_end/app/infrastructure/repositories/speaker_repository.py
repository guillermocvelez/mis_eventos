from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import Session, select
from app.domain.entities.speaker import Speaker
from app.domain.ports.speaker_repository import ISpeakerRepository
from app.infrastructure.orm.models import SpeakerORM


class SQLModelSpeakerRepository(ISpeakerRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, speaker: Speaker) -> Speaker:
        orm = SpeakerORM(
            id=speaker.id,
            name=speaker.name,
            bio=speaker.bio,
            email=speaker.email,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return speaker

    def find_by_id(self, speaker_id: UUID) -> Optional[Speaker]:
        result = self.db.get(SpeakerORM, speaker_id)
        if not result:
            return None
        return Speaker(
            id=result.id,
            name=result.name,
            bio=result.bio,
            email=result.email,
        )

    def find_all(self) -> list[Speaker]:
        results = self.db.exec(select(SpeakerORM)).all()
        return [
            Speaker(id=r.id, name=r.name, bio=r.bio, email=r.email)
            for r in results
        ]

    def update(self, speaker: Speaker) -> Speaker:
        orm = self.db.get(SpeakerORM, speaker.id)
        if orm:
            orm.name = speaker.name
            orm.bio = speaker.bio
            orm.email = speaker.email
            self.db.commit()
            self.db.refresh(orm)
        return speaker

    def delete(self, speaker_id: UUID) -> None:
        orm = self.db.get(SpeakerORM, speaker_id)
        if orm:
            self.db.delete(orm)
            self.db.commit()