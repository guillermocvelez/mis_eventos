import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, makeUser } from '@/__tests__/helpers'
import AdminUsersView from '@/views/admin/AdminUsersView.vue'
import { deleteUser, fetchUsers } from '@/services/usersApi'

vi.mock('@/services/usersApi', () => ({
  deleteUser: vi.fn(),
  fetchUsers: vi.fn(),
}))

const mockedDeleteUser = vi.mocked(deleteUser)
const mockedFetchUsers = vi.mocked(fetchUsers)

const user = makeUser()

function mountAdmin() {
  const pinia = activatePinia()

  return mount(AdminUsersView, {
    global: {
      plugins: [pinia],
      stubs: {
        AdminUserFilters: {
          props: ['searchQuery', 'roleFilter', 'statusFilter'],
          template:
            '<div><button data-test="role-filter" @click="$emit(\'update:roleFilter\', \'admin\')">role</button><button data-test="status-filter" @click="$emit(\'update:statusFilter\', \'inactive\')">status</button><button data-test="search-filter" @click="$emit(\'update:searchQuery\', \'ana\')">search</button></div>',
        },
        AdminUserFormModal: {
          props: ['isOpen', 'userId'],
          template:
            '<section data-test="form-modal">{{ isOpen ? `open:${userId || \'new\'}` : \'closed\' }}<button data-test="modal-close" @click="$emit(\'close\')">close</button><button data-test="modal-saved" @click="$emit(\'saved\')">saved</button></section>',
        },
        AdminUsersTable: {
          props: ['users'],
          template:
            '<div><button data-test="edit-user" @click="$emit(\'edit\', users[0].id)">edit</button><button data-test="delete-user" @click="$emit(\'delete\', users[0])">{{ users[0].email }}</button></div>',
        },
        UiPagination: {
          props: ['currentPage'],
          template: '<button data-test="page-change" @click="$emit(\'page-change\', 2)">page</button>',
        },
        UiToast: {
          props: ['message', 'open', 'variant'],
          template: '<div data-test="toast">{{ open ? `${variant}:${message}` : "" }}</div>',
        },
      },
    },
  })
}

describe('AdminUsersView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedFetchUsers.mockResolvedValue({
      items: [user],
      limit: 10,
      page: 1,
      pages: 1,
      total: 1,
    })
  })

  it('loads users on mount with default filters', async () => {
    const wrapper = mountAdmin()

    await flushPromises()

    expect(mockedFetchUsers).toHaveBeenCalledWith({
      is_active: undefined,
      limit: 10,
      page: 1,
      role: undefined,
      search: '',
    })
    expect(wrapper.text()).toContain('Gestión de usuarios')
    expect(wrapper.text()).toContain('ana@example.com')
  })

  it('deactivates users after confirmation and reloads the list', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    mockedDeleteUser.mockResolvedValue(undefined)

    const wrapper = mountAdmin()

    await flushPromises()
    await wrapper.get('[data-test="delete-user"]').trigger('click')
    await flushPromises()

    expect(window.confirm).toHaveBeenCalledWith('¿Quieres desactivar a ana@example.com?')
    expect(mockedDeleteUser).toHaveBeenCalledWith('user-1')
    expect(mockedFetchUsers).toHaveBeenCalledTimes(2)
  })

  it('does not delete users when confirmation is cancelled', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)

    const wrapper = mountAdmin()

    await flushPromises()
    await wrapper.get('[data-test="delete-user"]').trigger('click')

    expect(mockedDeleteUser).not.toHaveBeenCalled()
  })

  it('reloads users when role, status and page filters change', async () => {
    const wrapper = mountAdmin()

    await flushPromises()
    mockedFetchUsers.mockResolvedValue({
      items: [user],
      limit: 10,
      page: 2,
      pages: 2,
      total: 12,
    })
    await wrapper.get('[data-test="role-filter"]').trigger('click')
    await flushPromises()
    await wrapper.get('[data-test="status-filter"]').trigger('click')
    await flushPromises()
    await wrapper.get('[data-test="page-change"]').trigger('click')
    await flushPromises()

    expect(mockedFetchUsers).toHaveBeenLastCalledWith({
      is_active: false,
      limit: 10,
      page: 2,
      role: 'admin',
      search: '',
    })
  })

  it('debounces search before reloading users', async () => {
    vi.useFakeTimers()

    const wrapper = mountAdmin()

    await flushPromises()
    await wrapper.get('[data-test="search-filter"]').trigger('click')

    expect(mockedFetchUsers).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(350)
    await flushPromises()

    expect(mockedFetchUsers).toHaveBeenLastCalledWith(
      expect.objectContaining({
        page: 1,
        search: 'ana',
      }),
    )

    vi.useRealTimers()
  })

  it('renders load errors and retries', async () => {
    mockedFetchUsers.mockRejectedValueOnce(new Error('No pudimos cargar usuarios'))

    const wrapper = mountAdmin()

    await flushPromises()

    expect(wrapper.text()).toContain('No pudimos cargar usuarios')

    mockedFetchUsers.mockResolvedValueOnce({
      items: [user],
      limit: 10,
      page: 1,
      pages: 1,
      total: 1,
    })

    await wrapper.get('button.btn-secondary').trigger('click')
    await flushPromises()

    expect(mockedFetchUsers).toHaveBeenCalledTimes(2)
  })

  it('opens create and edit modals and closes them', async () => {
    const wrapper = mountAdmin()

    await flushPromises()
    await wrapper.get('.admin-topbar button').trigger('click')

    expect(wrapper.get('[data-test="form-modal"]').text()).toContain('open:new')

    await wrapper.get('[data-test="modal-close"]').trigger('click')

    expect(wrapper.get('[data-test="form-modal"]').text()).toContain('closed')

    await wrapper.get('[data-test="edit-user"]').trigger('click')

    expect(wrapper.get('[data-test="form-modal"]').text()).toContain('open:user-1')
  })

  it('shows success toast and reloads after form save', async () => {
    const wrapper = mountAdmin()

    await flushPromises()
    await wrapper.get('.admin-topbar button').trigger('click')
    await wrapper.get('[data-test="modal-saved"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-test="toast"]').text()).toContain('success:Usuario creado correctamente.')
    expect(mockedFetchUsers).toHaveBeenCalledTimes(2)
  })

  it('shows a danger toast when deactivation fails', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    mockedDeleteUser.mockRejectedValue(new Error('No se pudo desactivar'))

    const wrapper = mountAdmin()

    await flushPromises()
    await wrapper.get('[data-test="delete-user"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-test="toast"]').text()).toContain('danger:No se pudo desactivar')
  })
})
