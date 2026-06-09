# Backend - Mis Eventos

Backend construido con FastAPI, SQLModel, PostgreSQL y Alembic. La organizacion del codigo sigue una arquitectura por capas inspirada en puertos y adaptadores: el dominio no depende de FastAPI ni de la base de datos, y la infraestructura adapta esos detalles externos.

## Estructura general

```txt
app/
  main.py
  domain/
    entities/
    ports/
    exceptions.py
  application/
    dtos/
    use_cases/
  infrastructure/
    config.py
    db/
    orm/
    repositories/
    security/
    web/
      dependencies.py
      routers/
alembic/
tests/
```

## Capas de la arquitectura

### `domain/`

Contiene las reglas centrales del negocio.

- `entities/`: modelos de dominio con Pydantic. Ejemplos: `Event`, `User`, `Speaker`.
- `ports/`: interfaces abstractas que describen lo que el dominio necesita del exterior, como repositorios o servicios de seguridad.
- `exceptions.py`: excepciones propias del negocio, por ejemplo `EventNotFound`, `Unauthorized` o `CapacityExceeded`.

Esta capa no debe importar FastAPI, SQLModel ni detalles de base de datos.

### `application/`

Contiene los casos de uso y DTOs.

- `dtos/`: esquemas de entrada y salida usados por API y casos de uso.
- `use_cases/`: acciones del sistema, por ejemplo crear evento, actualizar usuario o registrar un asistente.

Los casos de uso orquestan reglas de negocio y usan puertos del dominio. Por ejemplo, `CreateEventUseCase` recibe un `IEventRepository`, valida reglas y devuelve un `EventDTO`.

### `infrastructure/`

Contiene adaptadores concretos hacia herramientas externas.

- `orm/models.py`: modelos SQLModel que representan tablas.
- `repositories/`: implementaciones SQLModel de los puertos del dominio.
- `db/session.py`: creacion de sesiones de base de datos.
- `web/routers/`: endpoints FastAPI.
- `web/dependencies.py`: inyeccion de dependencias para repositorios, usuario actual, roles y servicios.
- `security/`: implementaciones concretas de hashing y JWT.

Esta capa si puede importar FastAPI, SQLModel, librerias de seguridad y configuracion externa.

## Flujo de una peticion

Ejemplo simplificado para crear un ponente:

1. `app/main.py` registra el router de `speakers`.
2. `infrastructure/web/routers/speakers.py` recibe la peticion HTTP.
3. FastAPI inyecta el repositorio desde `infrastructure/web/dependencies.py`.
4. El router crea y ejecuta `CreateSpeakerUseCase`.
5. El caso de uso crea la entidad de dominio `Speaker`.
6. El caso de uso guarda usando el puerto `ISpeakerRepository`.
7. `SQLModelSpeakerRepository` persiste en la tabla `speakers`.
8. El caso de uso devuelve un `SpeakerDTO`.

La regla importante: el router traduce HTTP, el caso de uso ejecuta negocio y el repositorio habla con la base de datos.

## Agregar una nueva entidad

Usa este checklist cuando quieras agregar un nuevo recurso al backend. El ejemplo usa una entidad llamada `Sponsor`, pero aplica para cualquier entidad.

### 1. Crear la entidad de dominio

Crea un archivo en:

```txt
app/domain/entities/sponsor.py
```

Ejemplo:

```python
import uuid
from typing import Optional
from pydantic import BaseModel


class Sponsor(BaseModel):
    id: uuid.UUID
    name: str
    website: Optional[str] = None
```

Pon aqui metodos de negocio propios de la entidad si existen. Evita meter logica de HTTP o SQL.

### 2. Crear el puerto del repositorio

Crea:

```txt
app/domain/ports/sponsor_repository.py
```

Ejemplo:

```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.sponsor import Sponsor


class ISponsorRepository(ABC):
    @abstractmethod
    def save(self, sponsor: Sponsor) -> Sponsor:
        ...

    @abstractmethod
    def find_by_id(self, sponsor_id: UUID) -> Optional[Sponsor]:
        ...

    @abstractmethod
    def find_all(self) -> list[Sponsor]:
        ...

    @abstractmethod
    def update(self, sponsor: Sponsor) -> Sponsor:
        ...

    @abstractmethod
    def delete(self, sponsor_id: UUID) -> None:
        ...
```

El puerto define lo que la aplicacion necesita; todavia no habla de SQLModel.

### 3. Crear los DTOs

Crea:

```txt
app/application/dtos/sponsor_dto.py
```

Ejemplo:

```python
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SponsorCreateDTO(BaseModel):
    name: str
    website: Optional[str] = None


class SponsorUpdateDTO(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None


class SponsorDTO(BaseModel):
    id: UUID
    name: str
    website: Optional[str] = None
```

Los DTOs separan la entrada/salida de la API de la entidad de dominio.

### 4. Crear los casos de uso

Crea una carpeta:

```txt
app/application/use_cases/sponsors/
```

Archivos recomendados para CRUD basico:

```txt
create_sponsor.py
get_sponsors.py
update_sponsor.py
delete_sponsor.py
__init__.py
```

Ejemplo de creacion:

```python
from uuid import uuid4

from app.application.dtos.sponsor_dto import SponsorCreateDTO, SponsorDTO
from app.domain.entities.sponsor import Sponsor
from app.domain.ports.sponsor_repository import ISponsorRepository


class CreateSponsorUseCase:
    def __init__(self, sponsor_repo: ISponsorRepository):
        self.sponsor_repo = sponsor_repo

    def execute(self, dto: SponsorCreateDTO) -> SponsorDTO:
        sponsor = Sponsor(id=uuid4(), name=dto.name, website=dto.website)
        saved = self.sponsor_repo.save(sponsor)
        return SponsorDTO(id=saved.id, name=saved.name, website=saved.website)
```

Si el caso de uso valida reglas de negocio, lanza excepciones de `app/domain/exceptions.py`.

### 5. Agregar el modelo ORM

Edita:

```txt
app/infrastructure/orm/models.py
```

Ejemplo:

```python
class SponsorORM(SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "sponsors"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    website: Optional[str] = Field(default=None, max_length=255)
```

Este modelo representa la tabla. Aqui si se usan `SQLModel`, `Field`, indices, llaves foraneas y restricciones.

### 6. Implementar el repositorio SQLModel

Crea:

```txt
app/infrastructure/repositories/sponsor_repository.py
```

Ejemplo:

```python
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.domain.entities.sponsor import Sponsor
from app.domain.ports.sponsor_repository import ISponsorRepository
from app.infrastructure.orm.models import SponsorORM


class SQLModelSponsorRepository(ISponsorRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, sponsor: Sponsor) -> Sponsor:
        orm = SponsorORM(
            id=sponsor.id,
            name=sponsor.name,
            website=sponsor.website,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return sponsor

    def find_by_id(self, sponsor_id: UUID) -> Optional[Sponsor]:
        result = self.db.get(SponsorORM, sponsor_id)
        if not result:
            return None
        return Sponsor(id=result.id, name=result.name, website=result.website)

    def find_all(self) -> list[Sponsor]:
        results = self.db.exec(select(SponsorORM)).all()
        return [
            Sponsor(id=row.id, name=row.name, website=row.website)
            for row in results
        ]

    def update(self, sponsor: Sponsor) -> Sponsor:
        orm = self.db.get(SponsorORM, sponsor.id)
        if orm:
            orm.name = sponsor.name
            orm.website = sponsor.website
            self.db.commit()
            self.db.refresh(orm)
        return sponsor

    def delete(self, sponsor_id: UUID) -> None:
        orm = self.db.get(SponsorORM, sponsor_id)
        if orm:
            self.db.delete(orm)
            self.db.commit()
```

El repositorio convierte entre entidades de dominio y modelos ORM.

### 7. Registrar la dependencia

Edita:

```txt
app/infrastructure/web/dependencies.py
```

Agrega el import:

```python
from app.infrastructure.repositories.sponsor_repository import SQLModelSponsorRepository
```

Agrega el provider:

```python
def get_sponsor_repo(db: Session = Depends(get_db_session)):
    return SQLModelSponsorRepository(db)
```

Con esto los routers pueden recibir el repositorio usando `Depends(get_sponsor_repo)`.

### 8. Crear el router HTTP

Crea:

```txt
app/infrastructure/web/routers/sponsors.py
```

Ejemplo:

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.sponsor_dto import SponsorCreateDTO, SponsorDTO, SponsorUpdateDTO
from app.application.use_cases.sponsors.create_sponsor import CreateSponsorUseCase
from app.infrastructure.web.dependencies import get_current_user, get_sponsor_repo, require_role


router = APIRouter(prefix="/sponsors", tags=["sponsors"])


@router.post("/", response_model=SponsorDTO, status_code=status.HTTP_201_CREATED)
def create_sponsor(
    dto: SponsorCreateDTO,
    sponsor_repo=Depends(get_sponsor_repo),
    _=Depends(require_role("admin")),
):
    return CreateSponsorUseCase(sponsor_repo).execute(dto)
```

Completa los endpoints `GET`, `PATCH` y `DELETE` siguiendo el patron de `speakers.py`, `events.py` o `users.py`.

### 9. Registrar el router en `main.py`

Edita:

```txt
app/main.py
```

Agrega el import:

```python
from app.infrastructure.web.routers.sponsors import router as sponsors_router
```

Registra el router:

```python
app.include_router(sponsors_router)
```

Si el frontend corre en un puerto nuevo, agrega ese origen en la configuracion CORS.

### 10. Crear migracion de base de datos

Con los servicios arriba:

```bash
docker compose exec backend alembic revision --autogenerate -m "create sponsors"
```

Revisa el archivo generado en:

```txt
alembic/versions/
```

Luego aplica la migracion:

```bash
docker compose exec backend alembic upgrade head
```

### 11. Agregar datos seed si aplica

Si la entidad necesita datos iniciales, edita:

```txt
app/infrastructure/db/seed.py
```

Mantiene el seed idempotente cuando sea posible, para que se pueda ejecutar mas de una vez sin duplicar datos.

### 12. Agregar pruebas

Archivos sugeridos:

```txt
tests/domain/test_sponsor.py
tests/fakes/fake_sponsor_repository.py
tests/use_cases/test_sponsors.py
```

Prueba como minimo:

- Reglas de dominio de la entidad.
- Casos de uso exitosos.
- Casos de error y excepciones esperadas.
- Repositorio si agregaste consultas o persistencia no trivial.

Ejecuta:

```bash
docker compose exec backend pytest
```

## Checklist rapido

Para una entidad nueva, normalmente se tocan estos archivos:

```txt
app/domain/entities/<entidad>.py
app/domain/ports/<entidad>_repository.py
app/application/dtos/<entidad>_dto.py
app/application/use_cases/<entidades>/
app/infrastructure/orm/models.py
app/infrastructure/repositories/<entidad>_repository.py
app/infrastructure/web/dependencies.py
app/infrastructure/web/routers/<entidades>.py
app/main.py
alembic/versions/<revision>.py
tests/
```

## Comandos utiles

Levantar el backend con sus dependencias desde la raiz del proyecto:

```bash
docker compose up --build
```

Aplicar migraciones:

```bash
docker compose exec backend alembic upgrade head
```

Crear migracion:

```bash
docker compose exec backend alembic revision --autogenerate -m "nombre_de_la_migracion"
```

Ejecutar seed:

```bash
docker compose exec backend python -m app.infrastructure.db.seed
```

Ejecutar pruebas:

```bash
docker compose exec backend pytest
```

Ejecutar lint:

```bash
docker compose exec backend ruff check .
```
