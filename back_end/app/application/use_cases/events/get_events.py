import math
from app.application.dtos.event_dto import EventDTO, PaginatedEventsDTO
from app.domain.ports.event_repository import IEventRepository
from typing import Optional

class GetEventsUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(
        self,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        status=None
    ) -> PaginatedEventsDTO:

        events, total = self.event_repo.find_all(search=search, page=page, limit=limit, status=status)

        print(f"---------Status enviado en usecase: {status}")

        return PaginatedEventsDTO(
            items=[
                EventDTO(
                    id=e.id,
                    name=e.name,
                    description=e.description,
                    date=e.date,
                    end_date=e.end_date,
                    location=e.location,
                    capacity=e.capacity,
                    registered_count=e.registered_count,
                    status=e.status,
                    created_by=e.created_by,
                    created_at=e.created_at,
                )
                for e in events
            ],
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if total > 0 else 1,
        )