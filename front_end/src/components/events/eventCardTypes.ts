import type { EventStatus } from '@/stores/events'

export type CapacityTone = 'green' | 'muted' | 'red' | 'yellow'
export type EventBadgeVariant = 'danger' | 'info' | 'neutral' | 'success'

export type EventCardItem = {
  id: string
  title: string
  date: string
  endDate: string
  timeRange: string
  attendees: number
  capacity: number
  capacityPercent: number
  capacityTone: CapacityTone
  coverClass: string
  icon: string
  location: string
  status?: EventStatus | null
}
