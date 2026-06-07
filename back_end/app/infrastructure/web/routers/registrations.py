from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.registration_dto import RegistrationDTO
from app.application.dtos.event_dto import EventDTO
from app.application.use_cases.registrations.register_to_event import RegisterToEventUseCase
from app.application.use_cases.registrations.cancel_registration import CancelRegistrationUseCase
from app.application.use_cases.registrations.get_my_registrations import GetMyRegistrationsUseCase
from app.domain.exceptions import EventNotFound, CapacityExceeded, AlreadyRegistered
from app.infrastructure.web.dependencies import get_event_repo, get_registration_repo, get_current_user

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.post("/{event_id}", response_model=RegistrationDTO, status_code=status.HTTP_201_CREATED)
def register_to_event(
    event_id: UUID,
    event_repo=Depends(get_event_repo),
    registration_repo=Depends(get_registration_repo),
    current_user=Depends(get_current_user),
):
    try:
        return RegisterToEventUseCase(event_repo, registration_repo).execute(event_id, current_user.id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CapacityExceeded as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AlreadyRegistered as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(
    event_id: UUID,
    event_repo=Depends(get_event_repo),
    registration_repo=Depends(get_registration_repo),
    current_user=Depends(get_current_user),
):
    try:
        CancelRegistrationUseCase(event_repo, registration_repo).execute(event_id, current_user.id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AlreadyRegistered as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/me", response_model=list[EventDTO])
def get_my_registrations(
    registration_repo=Depends(get_registration_repo),
    current_user=Depends(get_current_user),
):
    return GetMyRegistrationsUseCase(registration_repo).execute(current_user.id)