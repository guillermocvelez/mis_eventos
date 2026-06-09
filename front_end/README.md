# Frontend - Mis Eventos

Frontend construido con Vue 3, Vite, TypeScript, Vue Router, Pinia y Vitest. La app consume la API del backend usando `VITE_API_BASE_URL` y organiza el codigo por responsabilidades: tipos, servicios HTTP, stores, vistas, componentes y estilos.

## Estructura general

```txt
src/
  main.ts
  App.vue
  router/
  stores/
  services/
  types/
  views/
    admin/
    auth/
    events/
    profile/
  components/
    admin/
    auth/
    events/
    ui/
  styles/
  design-system/
  __tests__/
```

## Capas del frontend

### `types/`

Contiene tipos TypeScript que representan contratos con el backend y modelos usados por la UI.

Ejemplos:

- `types/events.ts`: eventos, sesiones, ponentes, registros y payloads.
- `types/users.ts`: usuarios, roles, filtros y paginacion.
- `types/profile.ts`: datos del perfil.

Mantener estos tipos alineados con los DTOs del backend evita errores entre API y UI.

### `services/`

Contiene funciones HTTP puras para hablar con la API.

Ejemplos:

- `services/eventsApi.ts`
- `services/usersApi.ts`
- `services/profileApi.ts`

Responsabilidades de esta capa:

- Construir URLs usando `VITE_API_BASE_URL`.
- Adjuntar `Authorization` cuando el endpoint lo requiere.
- Serializar payloads con `JSON.stringify`.
- Leer mensajes de error del backend.
- Convertir respuestas JSON a tipos del proyecto.

Los services no deberian manejar estado de pantalla; eso vive en los stores o en las vistas.

### `stores/`

Contiene estado compartido con Pinia.

Ejemplos:

- `stores/auth.ts`: token, rol, login, registro, logout y permisos.
- `stores/events.ts`: lista de eventos, detalle, sesiones, registros, loading y errores.

Responsabilidades de esta capa:

- Mantener estado reutilizable entre vistas.
- Coordinar llamadas a `services/`.
- Exponer acciones con nombres de negocio.
- Normalizar datos cuando la UI necesita una forma mas comoda.

Si el estado solo se usa en una vista pequena, puede vivir localmente en esa vista.

### `views/`

Contiene pantallas conectadas a rutas.

Ejemplos:

- `views/events/EventsHomeView.vue`
- `views/events/EventDetailView.vue`
- `views/admin/AdminUsersView.vue`
- `views/auth/LoginView.vue`

Responsabilidades de esta capa:

- Leer parametros de ruta.
- Llamar stores o services.
- Componer componentes.
- Manejar flujo de pantalla, carga, vacios y errores.

### `components/`

Contiene piezas reutilizables de UI.

- `components/ui/`: sistema base de componentes reutilizables, como botones, inputs, modales, badges y paginacion.
- `components/events/`: componentes especificos de eventos.
- `components/admin/`: componentes especificos de administracion.
- `components/auth/`: componentes especificos de autenticacion.

Regla practica: si un componente conoce demasiado del dominio, va en su carpeta de dominio; si es visual y generico, va en `components/ui`.

### `router/`

Define rutas, lazy loading de vistas y guards de acceso.

El archivo principal es:

```txt
src/router/index.ts
```

Las rutas usan `meta` para reglas de acceso:

- `requiresAuth`: requiere usuario autenticado.
- `guestOnly`: solo login/registro cuando no hay sesion.
- `requiresManageEvents`: requiere rol `admin` u `organizer`.
- `requiresAdmin`: requiere rol `admin`.

El guard usa `useAuthStore()` para validar token, permisos y redirecciones.

### `styles/` y `design-system/`

Los estilos globales se importan desde:

```txt
src/styles/index.css
```

Ese archivo agrupa tokens, base y estilos por area:

```txt
tokens.css
base.css
components.css
auth.css
events.css
profile.css
```

`design-system/tokens.json` documenta tokens visuales del sistema de diseno.

## Flujo de datos

Ejemplo para cargar eventos:

1. `EventsHomeView.vue` solicita datos al `useEventsStore`.
2. `stores/events.ts` ejecuta `fetchEvents`.
3. El store llama `services/eventsApi.ts`.
4. El service arma la URL con `VITE_API_BASE_URL` y agrega el token.
5. El backend responde con `PaginatedEventsDTO`.
6. El store actualiza `items`, `page`, `total`, `isLoading` y `error`.
7. La vista renderiza componentes como `EventsGrid`, `EventCard`, `EventsToolbar` y estados de carga/error.

La regla importante: los componentes muestran UI, los stores manejan estado y los services hablan HTTP.

## Variables de entorno

El frontend usa:

```txt
VITE_API_BASE_URL=http://localhost:8000
```

En Docker Compose esta variable se pasa al contenedor `frontend`. Como Vite lee las variables al arrancar, si cambias `VITE_API_BASE_URL` debes recrear el frontend:

```bash
docker compose up -d --force-recreate frontend
```

Cuando corres el frontend fuera de Docker, puedes crear un `.env.local` dentro de `front_end/`:

```txt
VITE_API_BASE_URL=http://localhost:8000
```

## Agregar una nueva entidad

Usa este checklist cuando agregues una nueva seccion de UI conectada al backend. El ejemplo usa `Sponsor`, pero aplica para cualquier entidad.

### 1. Crear los tipos

Crea:

```txt
src/types/sponsors.ts
```

Ejemplo:

```ts
export type SponsorDTO = {
  id: string
  name: string
  website: string | null
}

export type SponsorCreatePayload = {
  name: string
  website?: string | null
}

export type SponsorUpdatePayload = Partial<SponsorCreatePayload>

export type PaginatedSponsorsDTO = {
  items: SponsorDTO[]
  total: number
  page: number
  limit: number
  pages: number
}

export type FetchSponsorsOptions = {
  limit?: number
  page?: number
  search?: string
}
```

Si el backend no devuelve paginacion para esa entidad, usa un tipo de lista simple.

### 2. Crear el service HTTP

Crea:

```txt
src/services/sponsorsApi.ts
```

Ejemplo:

```ts
import { useAuthStore } from '@/stores/auth'
import type {
  FetchSponsorsOptions,
  PaginatedSponsorsDTO,
  SponsorCreatePayload,
  SponsorDTO,
  SponsorUpdatePayload,
} from '@/types/sponsors'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
}

async function readErrorMessage(response: Response) {
  const fallback = 'No pudimos procesar la solicitud. Intentalo de nuevo.'

  try {
    const data: unknown = await response.json()
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string') return detail
    }
  } catch {
    return fallback
  }

  return fallback
}

async function fetchWithAuth(path: string, init: RequestInit = {}) {
  const authStore = useAuthStore()
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Authorization: authStore.authorizationHeader,
      ...init.headers,
    },
  })

  if (response.status === 401) {
    authStore.logout()
  }

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  return response
}

export async function fetchSponsors(options: Required<Pick<FetchSponsorsOptions, 'limit' | 'page'>> & FetchSponsorsOptions) {
  const params = new URLSearchParams({
    limit: String(options.limit),
    page: String(options.page),
  })

  if (options.search?.trim()) {
    params.set('search', options.search.trim())
  }

  const response = await fetchWithAuth(`/sponsors/?${params.toString()}`)
  return (await response.json()) as PaginatedSponsorsDTO
}

export async function createSponsor(payload: SponsorCreatePayload) {
  const response = await fetchWithAuth('/sponsors/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as SponsorDTO
}

export async function updateSponsor(sponsorId: string, payload: SponsorUpdatePayload) {
  const response = await fetchWithAuth(`/sponsors/${sponsorId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as SponsorDTO
}

export async function deleteSponsor(sponsorId: string) {
  await fetchWithAuth(`/sponsors/${sponsorId}`, {
    method: 'DELETE',
  })
}
```

Si el endpoint es publico, puedes omitir `Authorization`, pero manten el manejo de errores.

### 3. Crear el store si hay estado compartido

Crea:

```txt
src/stores/sponsors.ts
```

Ejemplo:

```ts
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  createSponsor as createSponsorRequest,
  deleteSponsor as deleteSponsorRequest,
  fetchSponsors as fetchSponsorsRequest,
  updateSponsor as updateSponsorRequest,
} from '@/services/sponsorsApi'
import type {
  FetchSponsorsOptions,
  SponsorCreatePayload,
  SponsorDTO,
  SponsorUpdatePayload,
} from '@/types/sponsors'

export const useSponsorsStore = defineStore('sponsors', () => {
  const items = ref<SponsorDTO[]>([])
  const total = ref(0)
  const page = ref(1)
  const limit = ref(10)
  const pages = ref(1)
  const search = ref('')
  const isLoading = ref(false)
  const error = ref('')

  const hasSponsors = computed(() => items.value.length > 0)

  async function fetchSponsors(options: FetchSponsorsOptions = {}) {
    isLoading.value = true
    error.value = ''

    const nextPage = options.page ?? page.value
    const nextLimit = options.limit ?? limit.value
    const nextSearch = options.search ?? search.value

    try {
      const data = await fetchSponsorsRequest({
        limit: nextLimit,
        page: nextPage,
        search: nextSearch,
      })

      items.value = data.items
      total.value = data.total
      page.value = data.page
      limit.value = data.limit
      pages.value = data.pages
      search.value = nextSearch
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      error.value = message || 'No pudimos cargar los patrocinadores.'
    } finally {
      isLoading.value = false
    }
  }

  async function createSponsor(payload: SponsorCreatePayload) {
    const sponsor = await createSponsorRequest(payload)
    items.value = [sponsor, ...items.value]
    return sponsor
  }

  async function updateSponsor(sponsorId: string, payload: SponsorUpdatePayload) {
    const sponsor = await updateSponsorRequest(sponsorId, payload)
    items.value = items.value.map((item) => (item.id === sponsor.id ? sponsor : item))
    return sponsor
  }

  async function deleteSponsor(sponsorId: string) {
    await deleteSponsorRequest(sponsorId)
    items.value = items.value.filter((item) => item.id !== sponsorId)
  }

  return {
    createSponsor,
    deleteSponsor,
    error,
    fetchSponsors,
    hasSponsors,
    isLoading,
    items,
    limit,
    page,
    pages,
    search,
    total,
    updateSponsor,
  }
})
```

Si la pantalla no comparte estado con otras rutas, puedes llamar el service directamente desde la vista.

### 4. Crear componentes de dominio

Crea una carpeta si la entidad tiene varias piezas de UI:

```txt
src/components/sponsors/
```

Ejemplos:

```txt
SponsorFormModal.vue
SponsorsTable.vue
SponsorFilters.vue
index.ts
```

Usa componentes de `components/ui/` para botones, inputs, modales, badges y paginacion. Asi la UI se mantiene consistente.

### 5. Crear la vista

Crea:

```txt
src/views/sponsors/SponsorsView.vue
```

La vista deberia:

- Cargar datos al montarse.
- Leer y actualizar filtros.
- Mostrar loading, error, vacio y contenido.
- Llamar acciones del store para crear, editar o borrar.
- Delegar tabla/formulario a componentes.

Para una vista administrativa, revisa `views/admin/AdminUsersView.vue`. Para una vista de dominio con detalle, revisa `views/events/EventDetailView.vue`.

### 6. Registrar la ruta

Edita:

```txt
src/router/index.ts
```

Ejemplo:

```ts
{
  path: '/patrocinadores',
  name: 'sponsors',
  component: () => import('@/views/sponsors/SponsorsView.vue'),
  meta: {
    requiresAuth: true,
    requiresAdmin: true,
  },
}
```

Elige el `meta` segun permisos:

- Solo usuarios autenticados: `requiresAuth`.
- Solo administradores: `requiresAdmin`.
- Organizadores o administradores: `requiresManageEvents`.
- Solo invitados: `guestOnly`.

### 7. Agregar navegacion si aplica

Si la nueva seccion debe aparecer en el menu lateral, revisa:

```txt
src/components/events/EventsSidebar.vue
```

Agrega el enlace respetando roles y rutas existentes.

### 8. Agregar estilos

Si puedes resolverlo con componentes UI y clases existentes, no agregues CSS nuevo.

Si necesitas estilos propios:

1. Crea o edita un archivo en `src/styles/`.
2. Importalo desde `src/styles/index.css`.
3. Usa nombres de clase claros y especificos del dominio.

### 9. Agregar pruebas

Archivos sugeridos:

```txt
src/services/__tests__/sponsorsApi.spec.ts
src/stores/__tests__/sponsors.spec.ts
src/views/__tests__/SponsorsView.spec.ts
src/components/sponsors/__tests__/SponsorsTable.spec.ts
```

Prueba como minimo:

- Service: URL, metodo HTTP, headers, payload y errores.
- Store: loading, errores y actualizacion de estado.
- Vista: render de loading, error, vacio y acciones principales.
- Componentes: eventos emitidos, props y estados visuales.

Usa helpers existentes en:

```txt
src/__tests__/helpers.ts
```

## Checklist rapido

Para una entidad nueva, normalmente se tocan estos archivos:

```txt
src/types/<entidades>.ts
src/services/<entidades>Api.ts
src/stores/<entidades>.ts
src/components/<entidades>/
src/views/<entidades>/<Entidad>View.vue
src/router/index.ts
src/components/events/EventsSidebar.vue
src/styles/
src/**/__tests__/
```

No todos son obligatorios. Si la entidad es muy simple, puede bastar con `types`, `service`, una `view`, ruta y pruebas.

## Comandos utiles

Instalar dependencias:

```bash
npm install
```

Correr en desarrollo:

```bash
npm run dev
```

Compilar y validar tipos:

```bash
npm run build
```

Ejecutar pruebas unitarias:

```bash
npm run test:unit
```

Ejecutar pruebas con coverage:

```bash
npm run test:coverage
```

Ejecutar lint:

```bash
npm run lint
```

Formatear `src/`:

```bash
npm run format
```

Desde Docker Compose, ejecuta los comandos dentro del contenedor:

```bash
docker compose exec frontend npm run test:unit
docker compose exec frontend npm run build
```
