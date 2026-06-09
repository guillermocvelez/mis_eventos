import uuid
from datetime import datetime
from app.domain.entities.user import User, UserRole


def make_user(**kwargs) -> User:
    defaults = dict(
        id=uuid.uuid4(),
        email="test@misEventos.com",
        name="Test User",
        hashed_password="hashed_1234",
        role=UserRole.attendee,
        is_active=True,
        created_at=datetime.utcnow()
    )
    defaults.update(kwargs)
    return User(**defaults)


def test_has_role_attendee():
    user = make_user(role=UserRole.attendee)
    assert user.has_role("attendee") is True


def test_has_role_organizer():
    user = make_user(role=UserRole.organizer)
    assert user.has_role("organizer") is True


def test_has_role_admin():
    user = make_user(role=UserRole.admin)
    assert user.has_role("admin") is True


def test_has_role_returns_false_for_wrong_role():
    user = make_user(role=UserRole.attendee)
    assert user.has_role("admin") is False


def test_has_role_returns_false_for_higher_role():
    user = make_user(role=UserRole.organizer)
    assert user.has_role("admin") is False
