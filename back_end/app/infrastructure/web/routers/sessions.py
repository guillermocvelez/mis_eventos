from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.session_dto import SessionCreateDTO, SessionUpdateDTO, SessionDTO
from app.application.use_cases.sessions.create_session import CreateSessionUseCase
from app.application.use_cases.sessions.get_sessions import GetSessionsUseCase
from app.application.use_cases.sessions.update_session import UpdateSessionUseCase
from app.application.use_cases.sessions.delete_session import DeleteSessionUseCase
from app.domain.exceptions import EventNotFound, SessionOverlap, InvalidEventDate, CapacityExceeded, Unauthorized
from app.infrastructure.web.dependencies import get_event_repo, get_session_repo, get_current_user, require_role

router = APIRouter(prefix="/events/{event_id}/sessions", tags=["sessions"])


@router.post("/", response_model=SessionDTO, status_code=status.HTTP_201_CREATED)
def create_session(
    event_id: UUID,
    dto: SessionCreateDTO,
    event_repo=Depends(get_event_repo),
    session_repo=Depends(get_session_repo),
    _=Depends(require_role("organizer", "admin")),
):
    try:
        return CreateSessionUseCase(event_repo, session_repo).execute(event_id, dto)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidEventDate, SessionOverlap, CapacityExceeded) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[SessionDTO])
def get_sessions(
    event_id: UUID,
    event_repo=Depends(get_event_repo),
    session_repo=Depends(get_session_repo),
    _=Depends(get_current_user),
):
    try:
        return GetSessionsUseCase(event_repo, session_repo).execute(event_id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{session_id}", response_model=SessionDTO)
def update_session(
    event_id: UUID,
    session_id: UUID,
    dto: SessionUpdateDTO,
    event_repo=Depends(get_event_repo),
    session_repo=Depends(get_session_repo),
    _=Depends(require_role("organizer", "admin")),
):
    try:
        return UpdateSessionUseCase(event_repo, session_repo).execute(event_id, session_id, dto)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidEventDate, SessionOverlap, CapacityExceeded) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Unauthorized as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    event_id: UUID,
    session_id: UUID,
    session_repo=Depends(get_session_repo),
    _=Depends(require_role("organizer", "admin")),
):
    try:
        DeleteSessionUseCase(session_repo).execute(session_id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))