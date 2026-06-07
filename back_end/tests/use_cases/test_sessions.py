import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.application.dtos.event_dto import EventCreateDTO
from app.application.dtos.session_dto import SessionCreateDTO, SessionUpdateDTO
from app.application.use_cases.events.create_event import CreateEventUseCase
from app.application.use_cases.sessions.create_session import CreateSessionUseCase
from app.application.use_cases.sessions.get_sessions import GetSessionsUseCase
from app.application.use_cases.sessions.update_session import UpdateSessionUseCase
from app.application.use_cases.sessions.delete_session import DeleteSessionUseCase
from app.domain.exceptions import (
    EventNotFound, SessionOverlap, SessionOutOfRange,
    InvalidEventDate, CapacityExceeded
)
from tests.fakes.fake_event_repository import FakeEventRepository
from tests.fakes.fake_session_repository import FakeSessionRepository
from tests.fakes.fake_speaker_repository import FakeSpeakerRepository


# ── Helpers ───────────────────────────────────────────────

def future(days=10, hour=10):
    base = datetime.now(timezone.utc) + timedelta(days=days)
    return base.replace(hour=hour, minute=0, second=0, microsecond=0)


def make_event_dto(**kwargs):
    defaults = {
        "name": "Evento Test",
        "date": future(days=5, hour=8),
        "end_date": future(days=5, hour=20),
        "capacity": 100,
    }
    return EventCreateDTO(**{**defaults, **kwargs})


def make_session_dto(**kwargs):
    defaults = {
        "title": "Sesión Test",
        "start_time": future(days=5, hour=10),
        "end_time": future(days=5, hour=12),
        "capacity": 50,
    }
    return SessionCreateDTO(**{**defaults, **kwargs})


# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture
def repos():
    return FakeEventRepository(), FakeSessionRepository(), FakeSpeakerRepository()


@pytest.fixture
def organizer_id():
    return uuid4()


@pytest.fixture
def evento(repos, organizer_id):
    event_repo, _, _ = repos
    return CreateEventUseCase(event_repo).execute(make_event_dto(), organizer_id)


# ── CreateSessionUseCase ──────────────────────────────────

class TestCreateSession:

    def test_crea_sesion_exitosamente(self, repos, evento):
        event_repo, session_repo, _ = repos
        result = CreateSessionUseCase(event_repo, session_repo).execute(evento.id, make_session_dto())

        assert result.title == "Sesión Test"
        assert result.event_id == evento.id

    def test_end_time_antes_de_start_time_lanza_excepcion(self, repos, evento):
        event_repo, session_repo, _ = repos
        dto = make_session_dto(
            start_time=future(days=5, hour=12),
            end_time=future(days=5, hour=10),
        )
        with pytest.raises(InvalidEventDate):
            CreateSessionUseCase(event_repo, session_repo).execute(evento.id, dto)

    def test_evento_inexistente_lanza_excepcion(self, repos):
        event_repo, session_repo, _ = repos
        with pytest.raises(EventNotFound):
            CreateSessionUseCase(event_repo, session_repo).execute(uuid4(), make_session_dto())

    def test_capacidad_mayor_al_evento_lanza_excepcion(self, repos, evento):
        event_repo, session_repo, _ = repos
        dto = make_session_dto(capacity=200)

        with pytest.raises(CapacityExceeded):
            CreateSessionUseCase(event_repo, session_repo).execute(evento.id, dto)

    def test_sesion_fuera_de_rango_del_evento_lanza_excepcion(self, repos, evento):
        event_repo, session_repo, _ = repos
        dto = make_session_dto(
            start_time=future(days=6, hour=21),
            end_time=future(days=6, hour=22),
        )
        with pytest.raises(SessionOutOfRange):
            CreateSessionUseCase(event_repo, session_repo).execute(evento.id, dto)

    def test_solapamiento_lanza_excepcion(self, repos, evento):
        event_repo, session_repo, _ = repos
        CreateSessionUseCase(event_repo, session_repo).execute(evento.id, make_session_dto())

        dto_solapado = make_session_dto(
            start_time=future(days=5, hour=11),
            end_time=future(days=5, hour=13),
        )
        with pytest.raises(SessionOverlap):
            CreateSessionUseCase(event_repo, session_repo).execute(evento.id, dto_solapado)


# ── GetSessionsUseCase ────────────────────────────────────

class TestGetSessions:

    def test_retorna_sesiones_del_evento(self, repos, evento):
        event_repo, session_repo, speaker_repo = repos
        CreateSessionUseCase(event_repo, session_repo).execute(evento.id, make_session_dto())

        result = GetSessionsUseCase(event_repo, session_repo, speaker_repo).execute(evento.id)

        assert len(result) == 1
        assert result[0].event_id == evento.id

    def test_evento_inexistente_lanza_excepcion(self, repos):
        event_repo, session_repo, speaker_repo = repos
        with pytest.raises(EventNotFound):
            GetSessionsUseCase(event_repo, session_repo, speaker_repo).execute(uuid4())

    def test_retorna_lista_vacia_si_no_hay_sesiones(self, repos, evento):
        event_repo, session_repo, speaker_repo = repos
        result = GetSessionsUseCase(event_repo, session_repo, speaker_repo).execute(evento.id)

        assert result == []


# ── UpdateSessionUseCase ──────────────────────────────────

class TestUpdateSession:

    def test_actualiza_titulo(self, repos, evento):
        event_repo, session_repo, _ = repos
        created = CreateSessionUseCase(event_repo, session_repo).execute(evento.id, make_session_dto())

        result = UpdateSessionUseCase(event_repo, session_repo).execute(
            evento.id, created.id, SessionUpdateDTO(title="Nuevo Título")
        )

        assert result.title == "Nuevo Título"
        assert result.capacity == 50  # no cambió

    def test_solapamiento_al_actualizar_lanza_excepcion(self, repos, evento):
        event_repo, session_repo, _ = repos
        CreateSessionUseCase(event_repo, session_repo).execute(
            evento.id,
            make_session_dto(start_time=future(days=5, hour=10), end_time=future(days=5, hour=12))
        )
        segunda = CreateSessionUseCase(event_repo, session_repo).execute(
            evento.id,
            make_session_dto(start_time=future(days=5, hour=13), end_time=future(days=5, hour=15))
        )

        with pytest.raises(SessionOverlap):
            UpdateSessionUseCase(event_repo, session_repo).execute(
                evento.id, segunda.id,
                SessionUpdateDTO(start_time=future(days=5, hour=11).replace(tzinfo=None))
            )

    def test_sesion_inexistente_lanza_excepcion(self, repos, evento):
        event_repo, session_repo, _ = repos
        with pytest.raises(EventNotFound):
            UpdateSessionUseCase(event_repo, session_repo).execute(
                evento.id, uuid4(), SessionUpdateDTO()
            )


# ── DeleteSessionUseCase ──────────────────────────────────

class TestDeleteSession:

    def test_elimina_sesion_existente(self, repos, evento):
        event_repo, session_repo, speaker_repo = repos
        created = CreateSessionUseCase(event_repo, session_repo).execute(evento.id, make_session_dto())

        DeleteSessionUseCase(session_repo).execute(created.id)

        result = GetSessionsUseCase(event_repo, session_repo, speaker_repo).execute(evento.id)
        assert result == []

    def test_sesion_inexistente_lanza_excepcion(self, repos):
        _, session_repo, _ = repos
        with pytest.raises(EventNotFound):
            DeleteSessionUseCase(session_repo).execute(uuid4())
