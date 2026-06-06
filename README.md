# Mis Eventos

## Correr el proyecto

Requisitos:

- Docker Desktop instalado y corriendo.

Para levantar backend y frontend en modo desarrollo:

```bash
docker compose up --build
```

Después del primer build, normalmente basta con:

```bash
docker compose up
```

Servicios disponibles:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Migraciones de base de datos

Crear una migración nueva:

```bash
docker compose exec backend alembic revision --autogenerate -m "nombre_de_la_migracion"
```

Aplicar migraciones pendientes:

```bash
docker compose exec backend alembic upgrade head
```

El proyecto queda con recarga en vivo:

- Los cambios en `front_end/` se reflejan con Vite.
- Los cambios en `back_end/` reinician FastAPI usando `fastapi dev`.

Para detener los contenedores:

```bash
docker compose down
```

## Dependencias Python

Las dependencias principales del backend van en:

```txt
back_end/requirements.txt
```

Las dependencias de desarrollo, pruebas y lint van en:

```txt
back_end/requirements-dev.txt
```

Si agregas una dependencia nueva, escríbela en el archivo correspondiente y reconstruye:

```bash
docker compose up --build
```
