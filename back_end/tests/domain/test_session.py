import uuid
from datetime import datetime
from app.domain.entities.session import EventSession


def make_session(start_hour: int, end_hour: int, **kwargs) -> EventSession:
    defaults = dict(
        id=uuid.uuid4(),
        event_id=uuid.uuid4(),
        title="Sesión de prueba",
        start_time=datetime(2025, 10, 1, start_hour, 0),
        end_time=datetime(2025, 10, 1, end_hour, 0)
    )
    defaults.update(kwargs)
    return EventSession(**defaults)


# ── overlaps_with ─────────────────────────────────────────────────────

def test_sessions_overlap_partially():
    # A: 09:00-11:00 / B: 10:00-12:00
    a = make_session(9, 11)
    b = make_session(10, 12)
    assert a.overlaps_with(b) is True


def test_sessions_consecutive_do_not_overlap():
    # A: 09:00-10:00 / B: 10:00-12:00
    a = make_session(9, 10)
    b = make_session(10, 12)
    assert a.overlaps_with(b) is False


def test_session_contained_inside_other_overlaps():
    # A: 09:00-13:00 / B: 10:00-11:00
    a = make_session(9, 13)
    b = make_session(10, 11)
    assert a.overlaps_with(b) is True


def test_sessions_completely_separate_do_not_overlap():
    # A: 09:00-10:00 / B: 11:00-12:00
    a = make_session(9, 10)
    b = make_session(11, 12)
    assert a.overlaps_with(b) is False


def test_overlap_is_symmetric():
    # Si A solapa con B, B debe solapar con A
    a = make_session(9, 11)
    b = make_session(10, 12)
    assert a.overlaps_with(b) == b.overlaps_with(a)