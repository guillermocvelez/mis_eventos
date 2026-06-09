import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ProfileView from '@/views/profile/ProfileView.vue'
import { fetchMyRegistrations } from '@/services/eventsApi'
import { fetchMyProfile } from '@/services/profileApi'
import type { EventDTO } from '@/types/events'
import type { UserProfileDTO } from '@/types/profile'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({
  name: 'profile' as string,
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({
    push: routerPush,
  }),
}))

vi.mock('@/services/eventsApi', () => ({
  fetchMyRegistrations: vi.fn(),
}))

vi.mock('@/services/profileApi', () => ({
  fetchMyProfile: vi.fn(),
}))

const mockedFetchMyProfile = vi.mocked(fetchMyProfile)
const mockedFetchMyRegistrations = vi.mocked(fetchMyRegistrations)

const profile: UserProfileDTO = {
  id: 'user-1',
  email: 'ana@example.com',
  name: 'Ana Gomez',
  role: 'admin',
  created_at: '2026-01-01T00:00:00Z',
  is_active: true,
  organized_count: 4,
  registered_count: 2,
}

const event: EventDTO = {
  id: 'event-1',
  name: 'Vue Conf',
  description: null,
  date: '2026-02-10T14:00:00Z',
  end_date: null,
  location: 'Bogota',
  capacity: 10,
  registered_count: 5,
  status: 'published',
  created_by: 'user-1',
  created_at: '2026-01-01T00:00:00Z',
}

function mountProfile() {
  return mount(ProfileView, {
    global: {
      stubs: {
        UiToast: { template: '<div />' },
      },
    },
  })
}

describe('ProfileView', () => {
  beforeEach(() => {
    routeState.name = 'profile'
    routerPush.mockReset()
    mockedFetchMyProfile.mockResolvedValue(profile)
    mockedFetchMyRegistrations.mockResolvedValue([event])
  })

  it('loads profile and registrations from the API', async () => {
    const wrapper = mountProfile()

    await flushPromises()

    expect(mockedFetchMyProfile).toHaveBeenCalled()
    expect(mockedFetchMyRegistrations).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Ana Gomez')
    expect(wrapper.text()).toContain('ana@example.com')
    expect(wrapper.text()).toContain('Vue Conf')
    expect(wrapper.text()).toContain('4')
  })

  it('shows empty state on the empty profile route and navigates to events', async () => {
    routeState.name = 'profile-empty'
    mockedFetchMyRegistrations.mockResolvedValue([])

    const wrapper = mountProfile()

    await flushPromises()
    await wrapper.get('button.btn-primary').trigger('click')

    expect(wrapper.text()).toContain('Aún no te has registrado en ningún evento')
    expect(routerPush).toHaveBeenCalledWith('/eventos')
  })
})
