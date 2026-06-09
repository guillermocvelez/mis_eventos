import type { UserRole } from './users'

export type UserProfileDTO = {
  id: string
  name: string
  email: string
  role: UserRole
  created_at: string
  is_active: boolean
  organized_count: number
  registered_count: number
}
