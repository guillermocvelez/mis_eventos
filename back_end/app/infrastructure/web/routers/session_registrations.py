from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.registration_dto import RegistrationDTO
from app.application.dtos.session_dto import SessionDTO
from app.application.use_cases.registrations.register_to_session import RegisterToSessionUseCase
from app.application.use_cases.registrations.cancel_session_registration import CancelSessionRegistrationUseCase
from app.application.use_cases.registrations.get_my_session_registrations import GetMySessionRegistrationsUseCase
from app.domain.exceptions import EventNotFound, CapacityExceeded, AlreadyRegistered
from app.infrastructure.web.dependencies import (
    get_registration_repo,
    get_session_repo,
    get_session_registration_repo,
    get_current_user,
)

router = APIRouter(prefix="/session-registrations", tags=["session-registrations"])


@router.post("/{session_id}", response_model=RegistrationDTO, status_code=status.HTTP_201_CREATED)
def register_to_session(
    session_id: UUID,
    registration_repo=Depends(get_registration_repo),
    session_repo=Depends(get_session_repo),
    session_registration_repo=Depends(get_session_registration_repo),
    current_user=Depends(get_current_user),
):
    try:
        result = RegisterToSessionUseCase(
            registration_repo, session_repo, session_registration_repo
        ).execute(session_id, current_user.id)
        return RegistrationDTO(
            id=result.id,
            user_id=result.user_id,
            event_id=result.session_id,
            registered_at=result.registered_at,
        )
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CapacityExceeded as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AlreadyRegistered as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_session_registration(
    session_id: UUID,
    session_repo=Depends(get_session_repo),
    session_registration_repo=Depends(get_session_registration_repo),
    current_user=Depends(get_current_user),
):
    try:
        CancelSessionRegistrationUseCase(
            session_repo, session_registration_repo
        ).execute(session_id, current_user.id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AlreadyRegistered as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/me", response_model=list[SessionDTO])
def get_my_session_registrations(
    session_registration_repo=Depends(get_session_registration_repo),
    current_user=Depends(get_current_user),
):
    return GetMySessionRegistrationsUseCase(session_registration_repo).execute(current_user.id)