export type UserRole = 'admin' | 'attendee' | 'organizer'

export type UserDTO = {
  id: string
  email: string
  name:string
  role: UserRole
  is_active: boolean
  created_at: string
}

export type UserCreatePayload = {
  email: string
  name:string
  password: string
  role: UserRole
  is_active: boolean
}

export type UserUpdatePayload = {
  email?: string
  name?:string
  password?: string
  role?: UserRole
  is_active?: boolean
}

export type PaginatedUsersDTO = {
  items: UserDTO[]
  total: number
  page: number
  limit: number
  pages: number
}

export type FetchUsersOptions = {
  is_active?: boolean
  limit?: number
  page?: number
  role?: UserRole
  search?: string
}
