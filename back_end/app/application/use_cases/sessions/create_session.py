from uuid import UUID
from app.application.dtos.session_dto import SessionCreateDTO, SessionDTO
from app.domain.entities.session import EventSession
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.session_repository import  ISessionRepository
from app.domain.exceptions import InvalidEventDate, SessionOutOfRange, SessionOverlap, EventNotFound, CapacityExceeded
import uuid


class CreateSessionUseCase:
    def __init__(self, event_repo: IEventRepository, session_repo: ISessionRepository):
        self.event_repo = event_repo
        self.session_repo = session_repo

    def execute(self, event_id: UUID, dto: SessionCreateDTO) -> SessionDTO:
        # 1. Verificar que end_time > start_time
        if dto.end_time <= dto.start_time:
            raise InvalidEventDate("La hora de fin debe ser posterior a la hora de inicio")

        # 2. Cargar el evento (verifica que existe y obtiene su capacidad)
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise EventNotFound(f"Evento {event_id} no encontrado")

  

        # 3. Verificar que capacity <= capacity del evento
        if dto.capacity is not None and event.capacity is not None:
            if dto.capacity > event.capacity:
                raise CapacityExceeded(
                    f"La capacidad de la sesión ({dto.capacity}) no puede superar "
                    f"la del evento ({event.capacity})"
                )

        # 4. Cargar sesiones existentes y verificar solapamiento
        existing_sessions = self.session_repo.find_by_event(event_id)

        start_time = dto.start_time.replace(tzinfo=None)
        end_time = dto.end_time.replace(tzinfo=None)

        new_session = EventSession(
            id=uuid.uuid4(),
            event_id=event_id,
            title=dto.title,
            speaker_id=dto.speaker_id, 
            start_time=start_time,
            end_time=end_time,
            capacity=dto.capacity,
        )

        if not event.session_is_within_range(new_session):
            raise SessionOutOfRange()

        for existing in existing_sessions:
            if new_session.overlaps_with(existing):
                raise SessionOverlap(
                    f"La sesión solapa con '{existing.title}' "
                    f"({existing.start_time.strftime('%H:%M')} - {existing.end_time.strftime('%H:%M')})"
                )

        # 5. Persistir y retornar
        saved = self.session_repo.save(new_session)

        return SessionDTO(
            id=saved.id,
            event_id=saved.event_id,
            title=saved.title,
            speaker_id=saved.speaker_id,
            start_time=saved.start_time,
            end_time=saved.end_time,
            capacity=saved.capacity,
            registered_count=saved.registered_count,
        )