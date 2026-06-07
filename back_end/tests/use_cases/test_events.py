import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.application.dtos.event_dto import EventCreateDTO, EventUpdateDTO
from app.application.use_cases.events.create_event import CreateEventUseCase
from app.application.use_cases.events.get_events import GetEventsUseCase
from app.application.use_cases.events.get_event_by_id import GetEventByIdUseCase
from app.application.use_cases.events.update_event import UpdateEventUseCase
from app.application.use_cases.events.delete_event import DeleteEventUseCase
from app.domain.exceptions import EventNotFound, Unauthorized, InvalidEventDate
from tests.fakes.fake_event_repository import FakeEventRepository


def future_date(days=10):
    return datetime.now(timezone.utc) + timedelta(days=days)


def make_dto(**kwargs):
    defaults = {
        "name": "Evento Test",
        "description": "Descripción",
        "date": future_date(),
        "location": "Manizales",
        "capacity": 100,
    }
    return EventCreateDTO(**{**defaults, **kwargs})


@pytest.fixture
def repo():
    return FakeEventRepository()


@pytest.fixture
def organizer_id():
    return uuid4()


# ── CreateEventUseCase ────────────────────────────────────

class TestCreateEvent:

    def test_crea_evento_exitosamente(self, repo, organizer_id):
        result = CreateEventUseCase(repo).execute(make_dto(), organizer_id)

        assert result.name == "Evento Test"
        assert result.capacity == 100
        assert result.created_by == organizer_id

    def test_estado_inicial_es_draft(self, repo, organizer_id):
        result = CreateEventUseCase(repo).execute(make_dto(), organizer_id)

        assert result.status.value == "draft"

    def test_fecha_pasada_lanza_excepcion(self, repo, organizer_id):
        dto = make_dto(date=datetime.now(timezone.utc) - timedelta(days=1))

        with pytest.raises(InvalidEventDate):
            CreateEventUseCase(repo).execute(dto, organizer_id)


# ── GetEventsUseCase ──────────────────────────────────────

class TestGetEvents:

    def _crear(self, repo, organizer_id, name="Evento Test"):
        CreateEventUseCase(repo).execute(make_dto(name=name), organizer_id)

    def test_retorna_lista_paginada(self, repo, organizer_id):
        self._crear(repo, organizer_id)
        self._crear(repo, organizer_id)

        result = GetEventsUseCase(repo).execute(page=1, limit=10)

        assert result.total == 2
        assert len(result.items) == 2

    def test_paginacion_limita_resultados(self, repo, organizer_id):
        for i in range(5):
            self._crear(repo, organizer_id, name=f"Evento {i}")

        result = GetEventsUseCase(repo).execute(page=1, limit=2)

        assert len(result.items) == 2
        assert result.total == 5
        assert result.pages == 3

    def test_busqueda_por_nombre(self, repo, organizer_id):
        self._crear(repo, organizer_id, name="Concierto Rock")
        self._crear(repo, organizer_id, name="Feria del Libro")

        result = GetEventsUseCase(repo).execute(search="Rock")

        assert result.total == 1
        assert result.items[0].name == "Concierto Rock"

    def test_sin_resultados_retorna_paginas_uno(self, repo):
        result = GetEventsUseCase(repo).execute()

        assert result.total == 0
        assert result.pages == 1


# ── GetEventByIdUseCase ───────────────────────────────────

class TestGetEventById:

    def test_retorna_evento_existente(self, repo, organizer_id):
        created = CreateEventUseCase(repo).execute(make_dto(), organizer_id)

        result = GetEventByIdUseCase(repo).execute(created.id)

        assert result.id == created.id

    def test_evento_inexistente_lanza_excepcion(self, repo):
        with pytest.raises(EventNotFound):
            GetEventByIdUseCase(repo).execute(uuid4())


# ── UpdateEventUseCase ────────────────────────────────────

class TestUpdateEvent:

    def test_actualiza_campos_enviados(self, repo, organizer_id):
        created = CreateEventUseCase(repo).execute(make_dto(), organizer_id)
        dto = EventUpdateDTO(name="Nombre Actualizado")

        result = UpdateEventUseCase(repo).execute(created.id, dto, organizer_id)

        assert result.name == "Nombre Actualizado"
        assert result.capacity == 100  # no cambió

    def test_usuario_no_propietario_lanza_unauthorized(self, repo, organizer_id):
        created = CreateEventUseCase(repo).execute(make_dto(), organizer_id)
        otro_user = uuid4()

        with pytest.raises(Unauthorized):
            UpdateEventUseCase(repo).execute(created.id, EventUpdateDTO(), otro_user)

    def test_evento_inexistente_lanza_not_found(self, repo, organizer_id):
        with pytest.raises(EventNotFound):
            UpdateEventUseCase(repo).execute(uuid4(), EventUpdateDTO(), organizer_id)


# ── DeleteEventUseCase ────────────────────────────────────

class TestDeleteEvent:

    def test_elimina_evento_existente(self, repo, organizer_id):
        created = CreateEventUseCase(repo).execute(make_dto(), organizer_id)

        DeleteEventUseCase(repo).execute(created.id, organizer_id)

        with pytest.raises(EventNotFound):
            GetEventByIdUseCase(repo).execute(created.id)

    def test_usuario_no_propietario_lanza_unauthorized(self, repo, organizer_id):
        created = CreateEventUseCase(repo).execute(make_dto(), organizer_id)

        with pytest.raises(Unauthorized):
            DeleteEventUseCase(repo).execute(created.id, uuid4())

    def test_evento_inexistente_lanza_not_found(self, repo, organizer_id):
        with pytest.raises(EventNotFound):
            DeleteEventUseCase(repo).execute(uuid4(), organizer_id)