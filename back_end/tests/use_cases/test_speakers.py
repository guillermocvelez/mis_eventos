import pytest
from uuid import uuid4

from app.application.dtos.speaker_dto import SpeakerCreateDTO, SpeakerUpdateDTO
from app.application.use_cases.speakers.create_speaker import CreateSpeakerUseCase
from app.application.use_cases.speakers.delete_speaker import DeleteSpeakerUseCase
from app.application.use_cases.speakers.get_speakers import GetSpeakersUseCase
from app.application.use_cases.speakers.update_speaker import UpdateSpeakerUseCase
from app.domain.exceptions import EventNotFound
from tests.fakes.fake_speaker_repository import FakeSpeakerRepository


def make_dto(**kwargs):
    defaults = {
        "name": "Speaker Test",
        "bio": "Bio",
        "email": "speaker@test.com",
    }
    return SpeakerCreateDTO(**{**defaults, **kwargs})


@pytest.fixture
def repo():
    return FakeSpeakerRepository()


class TestCreateSpeaker:

    def test_crea_speaker_exitosamente(self, repo):
        result = CreateSpeakerUseCase(repo).execute(make_dto())

        assert result.name == "Speaker Test"
        assert result.email == "speaker@test.com"
        assert repo.find_by_id(result.id) is not None


class TestGetSpeakers:

    def test_retorna_speakers(self, repo):
        CreateSpeakerUseCase(repo).execute(make_dto(name="Uno"))
        CreateSpeakerUseCase(repo).execute(make_dto(name="Dos"))

        result = GetSpeakersUseCase(repo).execute()

        assert len(result) == 2
        assert [s.name for s in result] == ["Uno", "Dos"]


class TestUpdateSpeaker:

    def test_actualiza_campos_enviados(self, repo):
        created = CreateSpeakerUseCase(repo).execute(make_dto())

        result = UpdateSpeakerUseCase(repo).execute(
            created.id,
            SpeakerUpdateDTO(name="Speaker Actualizado"),
        )

        assert result.name == "Speaker Actualizado"
        assert result.email == "speaker@test.com"

    def test_speaker_inexistente_lanza_not_found(self, repo):
        with pytest.raises(EventNotFound):
            UpdateSpeakerUseCase(repo).execute(uuid4(), SpeakerUpdateDTO(name="Nuevo"))


class TestDeleteSpeaker:

    def test_elimina_speaker_existente(self, repo):
        created = CreateSpeakerUseCase(repo).execute(make_dto())

        DeleteSpeakerUseCase(repo).execute(created.id)

        assert repo.find_by_id(created.id) is None

    def test_speaker_inexistente_lanza_not_found(self, repo):
        with pytest.raises(EventNotFound):
            DeleteSpeakerUseCase(repo).execute(uuid4())
