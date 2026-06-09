from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.dtos.event_dto import EventCreateDTO, EventUpdateDTO, EventDTO, PaginatedEventsDTO
from app.application.use_cases.events.create_event import CreateEventUseCase
from app.application.use_cases.events.get_events import GetEventsUseCase
from app.application.use_cases.events.get_event_by_id import GetEventByIdUseCase
from app.application.use_cases.events.update_event import UpdateEventUseCase
from app.application.use_cases.events.delete_event import DeleteEventUseCase
from app.domain.exceptions import EventNotFound, Unauthorized, InvalidEventDate
from app.infrastructure.web.dependencies import get_event_repo, get_current_user, require_role

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventDTO, status_code=status.HTTP_201_CREATED)
def create_event(
    dto: EventCreateDTO,
    event_repo=Depends(get_event_repo),
    current_user=Depends(require_role("organizer", "admin")),
):
    try:
        return CreateEventUseCase(event_repo).execute(dto, current_user.id)
    except InvalidEventDate as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=PaginatedEventsDTO)
def get_events(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None),
    event_repo=Depends(get_event_repo),
    _=Depends(get_current_user),
):
    return GetEventsUseCase(event_repo).execute(search=search, page=page, limit=limit, status=status)


@router.get("/{event_id}", response_model=EventDTO)
def get_event_by_id(
    event_id: UUID,
    event_repo=Depends(get_event_repo),
    _=Depends(get_current_user),
):
    try:
        return GetEventByIdUseCase(event_repo).execute(event_id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{event_id}", response_model=EventDTO)
def update_event(
    event_id: UUID,
    dto: EventUpdateDTO,
    event_repo=Depends(get_event_repo),
    current_user=Depends(get_current_user),
):
    try:
        return UpdateEventUseCase(event_repo).execute(event_id, dto, current_user.id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Unauthorized as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    event_repo=Depends(get_event_repo),
    current_user=Depends(require_role("organizer", "admin")),
):
    try:
        DeleteEventUseCase(event_repo).execute(event_id, current_user.id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Unauthorized as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))