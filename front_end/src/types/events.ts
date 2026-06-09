export type EventStatus = 'cancelled' | 'draft' | 'finished' | 'published'

export type EventDTO = {
  id: string
  name: string
  description: string | null
  date: string
  end_date: string | null
  location: string | null
  capacity: number
  registered_count: number
  status: EventStatus
  created_by: string
  created_at: string
}

export type EventCreatePayload = {
  name: string
  description?: string | null
  date: string
  end_date?: string | null
  location?: string | null
  capacity: number
}

export type EventUpdatePayload = Partial<EventCreatePayload> & {
  status?: EventStatus
}

export type RegistrationDTO = {
  id: string
  user_id: string
  event_id: string
  registered_at: string
}

export type EventRegistrantDTO = {
  user_id: string
  email: string
  role: string
  registered_at: string
}

export type SpeakerDTO = {
  id: string
  name: string
  bio: string | null
  email: string | null
}

export type SessionDTO = {
  id: string
  event_id: string
  title: string
  speaker: SpeakerDTO | null
  start_time: string
  end_time: string
  capacity: number | null
  registered_count: number
}

export type SessionCreatePayload = {
  title: string
  speaker_id?: string | null
  start_time: string
  end_time: string
  capacity?: number | null
}

export type SessionUpdatePayload = Partial<SessionCreatePayload>

export type PaginatedEventsDTO = {
  items: EventDTO[]
  total: number
  page: number
  limit: number
  pages: number
}

export type FetchEventsOptions = {
  limit?: number
  page?: number
  search?: string
  status?: EventStatus
}

export type EventDetailDTO = {
  event: EventDTO
  sessions: SessionDTO[]
}
