from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.event import Event, EventStatus
from app.domain.entities.registration import Registration
from app.domain.entities.session import EventSession
from app.domain.entities.session_registration import SessionRegistration
from app.domain.entities.speaker import Speaker
from app.domain.entities.user import User, UserRole
from app.infrastructure.repositories.event_repository import SQLModelEventRepository
from app.infrastructure.repositories.registration_repository import (
    SQLModelRegistrationRepository,
)
from app.infrastructure.repositories.session_registration_repository import (
    SQLModelSessionRegistrationRepository,
)
from app.infrastructure.repositories.session_repository import SQLModelSessionRepository
from app.infrastructure.repositories.speaker_repository import SQLModelSpeakerRepository
from app.infrastructure.repositories.user_repository import SQLModelUserRepository


def future(days=5, hour=10):
    base = datetime.now(timezone.utc) + timedelta(days=days)
    return base.replace(hour=hour, minute=0, second=0, microsecond=0)


def make_user(**kwargs):
    defaults = {
        "id": uuid4(),
        "email": f"{uuid4()}@test.com",
        "name": "User Test",
        "hashed_password": "hashed",
        "role": UserRole.attendee,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    return User(**{**defaults, **kwargs})


def make_event(created_by, **kwargs):
    defaults = {
        "id": uuid4(),
        "name": "Evento Test",
        "description": "Descripcion",
        "date": future(hour=8),
        "end_date": future(hour=20),
        "location": "Bogota",
        "capacity": 10,
        "registered_count": 0,
        "status": EventStatus.published,
        "created_by": created_by,
        "created_at": datetime.now(timezone.utc),
    }
    return Event(**{**defaults, **kwargs})


def make_session(event_id, **kwargs):
    defaults = {
        "id": uuid4(),
        "event_id": event_id,
        "title": "Sesion Test",
        "speaker_id": None,
        "start_time": future(hour=10).replace(tzinfo=None),
        "end_time": future(hour=12).replace(tzinfo=None),
        "capacity": 5,
        "registered_count": 0,
    }
    return EventSession(**{**defaults, **kwargs})


def make_registration(user_id, event_id, **kwargs):
    defaults = {
        "id": uuid4(),
        "user_id": user_id,
        "event_id": event_id,
        "registered_at": datetime.now(timezone.utc),
    }
    return Registration(**{**defaults, **kwargs})


def make_session_registration(user_id, session_id, **kwargs):
    defaults = {
        "id": uuid4(),
        "user_id": user_id,
        "session_id": session_id,
        "registered_at": datetime.now(timezone.utc),
    }
    return SessionRegistration(**{**defaults, **kwargs})


def test_user_repository_saves_finds_lists_updates_and_deactivates(db_session):
    repo = SQLModelUserRepository(db_session)
    attendee = repo.save(make_user(name="Ana Gomez", email="ana@test.com"))
    organizer = repo.save(
        make_user(
            name="Carlos Ruiz",
            email="carlos@test.com",
            role=UserRole.organizer,
        )
    )

    assert repo.find_by_email("ana@test.com").id == attendee.id
    assert repo.find_by_id(attendee.id).email == "ana@test.com"
    assert repo.find_by_email("missing@test.com") is None
    assert repo.find_by_id(uuid4()) is None

    users, total = repo.find_all(search="carlos", role=UserRole.organizer)
    assert total == 1
    assert users[0].id == organizer.id

    active_users, active_total = repo.find_all(is_active=True, page=1, limit=1)
    assert active_total == 2
    assert len(active_users) == 1

    updated = organizer.model_copy(update={"name": "Carlos Editado"})
    assert repo.update(updated).name == "Carlos Editado"

    repo.delete(attendee.id)
    assert repo.find_by_id(attendee.id).is_active is False


def test_event_repository_saves_queries_updates_deletes_and_counts(db_session):
    user_repo = SQLModelUserRepository(db_session)
    creator = user_repo.save(make_user(role=UserRole.organizer))
    other_creator = user_repo.save(make_user(role=UserRole.organizer))
    repo = SQLModelEventRepository(db_session)

    event = repo.save(make_event(creator.id, name="Conferencia Python"))
    repo.save(make_event(creator.id, name="Feria Vue", status=EventStatus.draft))
    repo.save(make_event(other_creator.id, name="Concierto"))

    assert repo.find_by_id(event.id).name == "Conferencia Python"
    assert repo.find_by_id(uuid4()) is None

    events, total = repo.find_all(search="python", status=EventStatus.published.value)
    assert total == 1
    assert events[0].id == event.id

    paged, paged_total = repo.find_all(page=1, limit=2)
    assert paged_total == 3
    assert len(paged) == 2

    updated = event.model_copy(
        update={"name": "Conferencia Python Editada", "registered_count": 2}
    )
    assert repo.update(updated).registered_count == 2
    assert repo.count_by_creator(creator.id) == 2

    repo.delete(event.id)
    assert repo.find_by_id(event.id) is None


def test_session_repository_saves_finds_updates_and_deletes(db_session):
    user = SQLModelUserRepository(db_session).save(make_user(role=UserRole.organizer))
    event = SQLModelEventRepository(db_session).save(make_event(user.id))
    repo = SQLModelSessionRepository(db_session)
    session = repo.save(make_session(event.id, title="Apertura"))

    assert repo.find_by_id(session.id).title == "Apertura"
    assert repo.find_by_id(uuid4()) is None
    assert repo.find_by_event(event.id)[0].id == session.id
    assert repo.find_by_event(uuid4()) == []

    updated = session.model_copy(update={"title": "Cierre", "registered_count": 1})
    assert repo.update(updated).title == "Cierre"

    repo.delete(session.id)
    assert repo.find_by_id(session.id) is None


def test_registration_repository_saves_queries_joins_and_deletes(db_session):
    user_repo = SQLModelUserRepository(db_session)
    user = user_repo.save(make_user(email="registrado@test.com"))
    creator = user_repo.save(make_user(role=UserRole.organizer))
    event = SQLModelEventRepository(db_session).save(make_event(creator.id))
    repo = SQLModelRegistrationRepository(db_session)
    registration = repo.save(make_registration(user.id, event.id))

    assert repo.find_by_user_and_event(user.id, event.id).id == registration.id
    assert repo.find_by_user_and_event(uuid4(), event.id) is None

    events = repo.find_by_user(user.id)
    assert len(events) == 1
    assert events[0].id == event.id

    registrants = repo.find_users_by_event(event.id)
    assert len(registrants) == 1
    assert registrants[0].email == "registrado@test.com"

    repo.delete(user.id, event.id)
    assert repo.find_by_user_and_event(user.id, event.id) is None


def test_session_registration_repository_saves_queries_and_deletes(db_session):
    user_repo = SQLModelUserRepository(db_session)
    user = user_repo.save(make_user())
    creator = user_repo.save(make_user(role=UserRole.organizer))
    event = SQLModelEventRepository(db_session).save(make_event(creator.id))
    session = SQLModelSessionRepository(db_session).save(make_session(event.id))
    repo = SQLModelSessionRegistrationRepository(db_session)
    registration = repo.save(make_session_registration(user.id, session.id))

    assert repo.find_by_user_and_session(user.id, session.id).id == registration.id
    assert repo.find_by_user_and_session(uuid4(), session.id) is None

    sessions = repo.find_by_user(user.id)
    assert len(sessions) == 1
    assert sessions[0].id == session.id

    repo.delete(user.id, session.id)
    assert repo.find_by_user_and_session(user.id, session.id) is None

    repo.delete(user.id, session.id)


def test_speaker_repository_saves_finds_lists_updates_and_deletes(db_session):
    repo = SQLModelSpeakerRepository(db_session)
    speaker = repo.save(
        Speaker(
            id=uuid4(),
            name="Speaker Test",
            bio="Bio",
            email="speaker@test.com",
        )
    )

    assert repo.find_by_id(speaker.id).email == "speaker@test.com"
    assert repo.find_by_id(uuid4()) is None
    assert repo.find_all()[0].id == speaker.id

    updated = speaker.model_copy(update={"name": "Speaker Editado"})
    assert repo.update(updated).name == "Speaker Editado"

    repo.delete(speaker.id)
    assert repo.find_by_id(speaker.id) is None

    repo.update(updated)
    repo.delete(speaker.id)
