# Mis Eventos

Proyecto de microservicios para gestionar eventos. El entorno local se levanta con Docker Compose y queda dividido en tres servicios:

- `frontend`: aplicacion Vue + Vite.
- `backend`: API FastAPI.
- `postgres`: base de datos PostgreSQL.

## Requisitos

- Docker Desktop instalado y corriendo.
- Git para clonar el repositorio.

No necesitas instalar Node, Python ni PostgreSQL en tu maquina para correr el proyecto con Docker.

## Configuracion inicial

Copia el archivo de ejemplo de variables de entorno:

```bash
cp .env.example .env
```

El archivo `.env` controla la conexion entre servicios y la URL publica que usa el frontend para llamar al backend:

```txt
DATABASE_URL=postgresql://mis_eventos:mis_eventos@postgres:5432/mis_eventos
VITE_API_BASE_URL=http://localhost:8000

POSTGRES_USER=mis_eventos
POSTGRES_PASSWORD=mis_eventos
POSTGRES_DB=mis_eventos
```

Notas importantes:

- `DATABASE_URL` usa el host `postgres` porque el backend se conecta a la base de datos dentro de la red de Docker Compose.
- `VITE_API_BASE_URL` usa `http://localhost:8000` porque el navegador corre fuera de Docker y accede al backend por el puerto publicado en tu maquina.
- Si cambias `VITE_API_BASE_URL`, reinicia el contenedor del frontend para que Vite tome el nuevo valor.

## Correr el proyecto

Para levantar los microservicios en modo desarrollo:

```bash
docker compose up --build
```

Después del primer build, normalmente basta con:

```bash
docker compose up
```

El proyecto queda con recarga en vivo:

- Los cambios en `front_end/` se reflejan con Vite.
- Los cambios en `back_end/` reinician FastAPI usando `fastapi dev`.

Servicios disponibles al levantar Compose:

| Servicio | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Documentacion API | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

Para detener los contenedores:

```bash
docker compose down
```

Para detenerlos y borrar los volumenes de datos locales:

```bash
docker compose down -v
```

Usa `down -v` solamente cuando quieras reiniciar la base de datos desde cero.

## Flujo recomendado desde cero

Levanta los servicios:

```bash
docker compose up --build
```

En otra terminal, aplica migraciones pendientes:

```bash
docker compose exec backend alembic upgrade head
```

Carga datos iniciales:

```bash
docker compose exec backend python -m app.infrastructure.db.seed
```

Luego abre el frontend en http://localhost:5173.

## Migraciones de base de datos

Crear una migración nueva:

```bash
docker compose exec backend alembic revision --autogenerate -m "nombre_de_la_migracion"
```

Aplicar migraciones pendientes:

```bash
docker compose exec backend alembic upgrade head
```

Ejecutar el seed de datos iniciales:

```bash
docker compose exec backend python -m app.infrastructure.db.seed
```

## Comandos utiles

Ver logs de todos los servicios:

```bash
docker compose logs -f
```

Ver logs de un servicio especifico:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Recrear solamente el frontend despues de cambiar `VITE_API_BASE_URL`:

```bash
docker compose up -d --force-recreate frontend
```

Entrar al contenedor del backend:

```bash
docker compose exec backend bash
```

Entrar al contenedor del frontend:

```bash
docker compose exec frontend sh
```

## Pruebas y calidad

Ejecutar pruebas del backend:

```bash
docker compose exec backend pytest
```

Ejecutar lint del backend:

```bash
docker compose exec backend ruff check .
```

Ejecutar pruebas del frontend:

```bash
docker compose exec frontend npm run test:unit
```

Ejecutar validacion de tipos y build del frontend:

```bash
docker compose exec frontend npm run build
```

## Dependencias Python

Las dependencias del backend van en:

```txt
back_end/requirements.txt
```

Si agregas una dependencia nueva, escríbela en el archivo correspondiente y reconstruye:

```bash
docker compose up --build
```

## Dependencias frontend

Las dependencias del frontend van en:

```txt
front_end/package.json
```

Si agregas una dependencia nueva, instalala dentro del contenedor o desde la carpeta `front_end/`, y luego reconstruye si es necesario:

```bash
docker compose exec frontend npm install nombre_paquete
docker compose up --build frontend
```
