import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.application.use_cases.registrations.cancel_registration import (
    CancelRegistrationUseCase,
)
from app.application.use_cases.registrations.cancel_session_registration import (
    CancelSessionRegistrationUseCase,
)
from app.application.use_cases.registrations.get_my_registrations import (
    GetMyRegistrationsUseCase,
)
from app.application.use_cases.registrations.get_my_session_registrations import (
    GetMySessionRegistrationsUseCase,
)
from app.application.use_cases.registrations.register_to_event import (
    RegisterToEventUseCase,
)
from app.application.use_cases.registrations.register_to_session import (
    RegisterToSessionUseCase,
)
from app.domain.entities.event import Event
from app.domain.entities.session import EventSession
from app.domain.exceptions import (
    AlreadyRegistered,
    CapacityExceeded,
    EventNotFound,
    RegistrationNotFound,
)
from tests.fakes.fake_event_repository import FakeEventRepository
from tests.fakes.fake_registration_repository import FakeRegistrationRepository
from tests.fakes.fake_session_registration_repository import (
    FakeSessionRegistrationRepository,
)
from tests.fakes.fake_session_repository import FakeSessionRepository


def future(days=5, hour=10):
    base = datetime.now(timezone.utc) + timedelta(days=days)
    return base.replace(hour=hour, minute=0, second=0, microsecond=0)


def make_event(**kwargs):
    defaults = {
        "id": uuid4(),
        "name": "Evento Test",
        "date": future(hour=8),
        "end_date": future(hour=20),
        "capacity": 10,
        "registered_count": 0,
        "created_by": uuid4(),
        "created_at": datetime.now(timezone.utc),
    }
    return Event(**{**defaults, **kwargs})


def make_session(event_id, **kwargs):
    defaults = {
        "id": uuid4(),
        "event_id": event_id,
        "title": "Sesion Test",
        "start_time": future(hour=10).replace(tzinfo=None),
        "end_time": future(hour=12).replace(tzinfo=None),
        "capacity": 5,
        "registered_count": 0,
    }
    return EventSession(**{**defaults, **kwargs})


@pytest.fixture
def repos():
    return (
        FakeEventRepository(),
        FakeRegistrationRepository(),
        FakeSessionRepository(),
        FakeSessionRegistrationRepository(),
    )


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def event(repos):
    event_repo, registration_repo, _, _ = repos
    event = make_event()
    event_repo.save(event)
    registration_repo.add_event(event)
    return event


@pytest.fixture
def session(repos, event):
    _, _, session_repo, session_registration_repo = repos
    session = make_session(event.id)
    session_repo.save(session)
    session_registration_repo.add_session(session)
    return session


class TestRegisterToEvent:

    def test_registra_usuario_en_evento(self, repos, event, user_id):
        event_repo, registration_repo, _, _ = repos

        result = RegisterToEventUseCase(event_repo, registration_repo).execute(
            event.id,
            user_id,
        )

        assert result.user_id == user_id
        assert result.event_id == event.id
        assert event_repo.find_by_id(event.id).registered_count == 1

    def test_evento_inexistente_lanza_not_found(self, repos, user_id):
        event_repo, registration_repo, _, _ = repos

        with pytest.raises(EventNotFound):
            RegisterToEventUseCase(event_repo, registration_repo).execute(
                uuid4(),
                user_id,
            )

    def test_evento_sin_capacidad_lanza_excepcion(self, repos, user_id):
        event_repo, registration_repo, _, _ = repos
        event = make_event(capacity=1, registered_count=1)
        event_repo.save(event)

        with pytest.raises(CapacityExceeded):
            RegisterToEventUseCase(event_repo, registration_repo).execute(
                event.id,
                user_id,
            )

    def test_usuario_ya_registrado_lanza_excepcion(self, repos, event, user_id):
        event_repo, registration_repo, _, _ = repos
        use_case = RegisterToEventUseCase(event_repo, registration_repo)
        use_case.execute(event.id, user_id)

        with pytest.raises(AlreadyRegistered):
            use_case.execute(event.id, user_id)


class TestCancelRegistration:

    def test_cancela_registro_existente(self, repos, event, user_id):
        event_repo, registration_repo, _, _ = repos
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)

        CancelRegistrationUseCase(event_repo, registration_repo).execute(
            event.id,
            user_id,
        )

        assert registration_repo.find_by_user_and_event(user_id, event.id) is None
        assert event_repo.find_by_id(event.id).registered_count == 0

    def test_registro_inexistente_lanza_excepcion(self, repos, event, user_id):
        event_repo, registration_repo, _, _ = repos

        with pytest.raises(RegistrationNotFound):
            CancelRegistrationUseCase(event_repo, registration_repo).execute(
                event.id,
                user_id,
            )


class TestGetMyRegistrations:

    def test_retorna_eventos_del_usuario(self, repos, event, user_id):
        event_repo, registration_repo, _, _ = repos
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)

        result = GetMyRegistrationsUseCase(registration_repo).execute(user_id)

        assert len(result) == 1
        assert result[0].id == event.id


class TestRegisterToSession:

    def test_registra_usuario_en_sesion(self, repos, event, session, user_id):
        event_repo, registration_repo, session_repo, session_registration_repo = repos
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)

        result = RegisterToSessionUseCase(
            registration_repo,
            session_repo,
            session_registration_repo,
        ).execute(session.id, user_id)

        assert result.user_id == user_id
        assert result.session_id == session.id
        assert session_repo.find_by_id(session.id).registered_count == 1

    def test_sesion_inexistente_lanza_not_found(self, repos, user_id):
        _, registration_repo, session_repo, session_registration_repo = repos

        with pytest.raises(EventNotFound):
            RegisterToSessionUseCase(
                registration_repo,
                session_repo,
                session_registration_repo,
            ).execute(uuid4(), user_id)

    def test_sin_registro_al_evento_lanza_excepcion(self, repos, session, user_id):
        _, registration_repo, session_repo, session_registration_repo = repos

        with pytest.raises(AlreadyRegistered):
            RegisterToSessionUseCase(
                registration_repo,
                session_repo,
                session_registration_repo,
            ).execute(session.id, user_id)

    def test_sesion_sin_capacidad_lanza_excepcion(self, repos, event, user_id):
        event_repo, registration_repo, session_repo, session_registration_repo = repos
        session = make_session(event.id, capacity=1, registered_count=1)
        session_repo.save(session)
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)

        with pytest.raises(CapacityExceeded):
            RegisterToSessionUseCase(
                registration_repo,
                session_repo,
                session_registration_repo,
            ).execute(session.id, user_id)

    def test_usuario_ya_registrado_lanza_excepcion(self, repos, event, session, user_id):
        event_repo, registration_repo, session_repo, session_registration_repo = repos
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)
        use_case = RegisterToSessionUseCase(
            registration_repo,
            session_repo,
            session_registration_repo,
        )
        use_case.execute(session.id, user_id)

        with pytest.raises(AlreadyRegistered):
            use_case.execute(session.id, user_id)


class TestCancelSessionRegistration:

    def test_cancela_registro_a_sesion(self, repos, event, session, user_id):
        event_repo, registration_repo, session_repo, session_registration_repo = repos
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)
        RegisterToSessionUseCase(
            registration_repo,
            session_repo,
            session_registration_repo,
        ).execute(session.id, user_id)

        CancelSessionRegistrationUseCase(
            session_repo,
            session_registration_repo,
        ).execute(session.id, user_id)

        assert session_registration_repo.find_by_user_and_session(user_id, session.id) is None
        assert session_repo.find_by_id(session.id).registered_count == 0

    def test_sesion_inexistente_lanza_not_found(self, repos, user_id):
        _, _, session_repo, session_registration_repo = repos

        with pytest.raises(EventNotFound):
            CancelSessionRegistrationUseCase(
                session_repo,
                session_registration_repo,
            ).execute(uuid4(), user_id)

    def test_registro_inexistente_lanza_excepcion(self, repos, session, user_id):
        _, _, session_repo, session_registration_repo = repos

        with pytest.raises(AlreadyRegistered):
            CancelSessionRegistrationUseCase(
                session_repo,
                session_registration_repo,
            ).execute(session.id, user_id)


class TestGetMySessionRegistrations:

    def test_retorna_sesiones_del_usuario(self, repos, event, session, user_id):
        event_repo, registration_repo, session_repo, session_registration_repo = repos
        RegisterToEventUseCase(event_repo, registration_repo).execute(event.id, user_id)
        RegisterToSessionUseCase(
            registration_repo,
            session_repo,
            session_registration_repo,
        ).execute(session.id, user_id)

        result = GetMySessionRegistrationsUseCase(session_registration_repo).execute(user_id)

        assert len(result) == 1
        assert result[0].id == session.id
