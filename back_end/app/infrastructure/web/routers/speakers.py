from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.speaker_dto import SpeakerCreateDTO, SpeakerUpdateDTO, SpeakerDTO
from app.application.use_cases.speakers.create_speaker import CreateSpeakerUseCase
from app.application.use_cases.speakers.get_speakers import GetSpeakersUseCase
from app.application.use_cases.speakers.update_speaker import UpdateSpeakerUseCase
from app.application.use_cases.speakers.delete_speaker import DeleteSpeakerUseCase
from app.domain.exceptions import EventNotFound
from app.infrastructure.web.dependencies import get_speaker_repo, get_current_user, require_role

router = APIRouter(prefix="/speakers", tags=["speakers"])


@router.post("/", response_model=SpeakerDTO, status_code=status.HTTP_201_CREATED)
def create_speaker(
    dto: SpeakerCreateDTO,
    speaker_repo=Depends(get_speaker_repo),
    _=Depends(require_role("admin")),
):
    return CreateSpeakerUseCase(speaker_repo).execute(dto)


@router.get("/", response_model=list[SpeakerDTO])
def get_speakers(
    speaker_repo=Depends(get_speaker_repo),
    _=Depends(get_current_user),
):
    return GetSpeakersUseCase(speaker_repo).execute()


@router.patch("/{speaker_id}", response_model=SpeakerDTO)
def update_speaker(
    speaker_id: UUID,
    dto: SpeakerUpdateDTO,
    speaker_repo=Depends(get_speaker_repo),
    _=Depends(require_role("admin")),
):
    try:
        return UpdateSpeakerUseCase(speaker_repo).execute(speaker_id, dto)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{speaker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speaker(
    speaker_id: UUID,
    speaker_repo=Depends(get_speaker_repo),
    _=Depends(require_role("admin")),
):
    try:
        DeleteSpeakerUseCase(speaker_repo).execute(speaker_id)
    except EventNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))