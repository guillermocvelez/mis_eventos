from uuid import UUID
from app.application.dtos.session_dto import SessionUpdateDTO, SessionDTO
from app.domain.entities.session import EventSession
from app.domain.ports.event_repository import IEventRepository
from app.domain.ports.session_repository import ISessionRepository
from app.domain.exceptions import EventNotFound, SessionOverlap, InvalidEventDate, CapacityExceeded


class UpdateSessionUseCase:
    def __init__(self, event_repo: IEventRepository, session_repo: ISessionRepository):
        self.event_repo = event_repo
        self.session_repo = session_repo

    def execute(self, event_id: UUID, session_id: UUID, dto: SessionUpdateDTO) -> SessionDTO:
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise EventNotFound(f"Evento {event_id} no encontrado")

        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise EventNotFound(f"Sesión {session_id} no encontrada")

        # Aplicar cambios sobre los valores actuales
        updated = session.model_copy(update={
            k: v for k, v in dto.model_dump().items() if v is not None
        })

        # Validar end_time > start_time con los valores finales
        if updated.end_time <= updated.start_time:
            raise InvalidEventDate("La hora de fin debe ser posterior a la hora de inicio")

        # Validar capacity contra el evento
        if updated.capacity is not None and event.capacity is not None:
            if updated.capacity > event.capacity:
                raise CapacityExceeded(
                    f"La capacidad de la sesión ({updated.capacity}) no puede superar "
                    f"la del evento ({event.capacity})"
                )

        # Verificar solapamiento excluyendo la sesión que estamos editando
        existing_sessions = self.session_repo.find_by_event(event_id)
        others = [s for s in existing_sessions if s.id != session_id]

        for other in others:
            if updated.overlaps_with(other):
                raise SessionOverlap(
                    f"La sesión solapa con '{other.title}' "
                    f"({other.start_time.strftime('%H:%M')} - {other.end_time.strftime('%H:%M')})"
                )

        saved = self.session_repo.update(updated)

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
