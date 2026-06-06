import uuid
from datetime import datetime
from app.domain.entities.event import Event, EventStatus


def make_event(**kwargs) -> Event:
    """Factory para no repetir código en cada test."""
    defaults = dict(
        id=uuid.uuid4(),
        name="Summit de Innovación",
        date=datetime(2025, 10, 1),
        capacity=100,
        registered_count=0,
        status=EventStatus.published,
        created_by=uuid.uuid4(),
        created_at=datetime.utcnow()
    )
    defaults.update(kwargs)
    return Event(**defaults)


# ── has_capacity ──────────────────────────────────────────────────────

def test_has_capacity_when_empty():
    event = make_event(capacity=100, registered_count=0)
    assert event.has_capacity() is True


def test_has_capacity_when_partially_full():
    event = make_event(capacity=100, registered_count=50)
    assert event.has_capacity() is True


def test_has_capacity_when_full():
    event = make_event(capacity=100, registered_count=100)
    assert event.has_capacity() is False


def test_has_capacity_when_one_spot_left():
    event = make_event(capacity=100, registered_count=99)
    assert event.has_capacity() is True


# ── can_be_edited_by ──────────────────────────────────────────────────

def test_can_be_edited_by_creator():
    creator_id = uuid.uuid4()
    event = make_event(created_by=creator_id)
    assert event.can_be_edited_by(creator_id) is True


def test_cannot_be_edited_by_other_user():
    event = make_event(created_by=uuid.uuid4())
    assert event.can_be_edited_by(uuid.uuid4()) is False


def test_cannot_be_edited_by_random_uuid():
    event = make_event(created_by=uuid.uuid4())
    assert event.can_be_edited_by(uuid.uuid4()) is False