import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AdminUserFormModal from '../AdminUserFormModal.vue'
import { createUser, fetchUserById, updateUser } from '@/services/usersApi'

vi.mock('@/services/usersApi', () => ({
  createUser: vi.fn(),
  fetchUserById: vi.fn(),
  updateUser: vi.fn(),
}))

const mockedCreateUser = vi.mocked(createUser)
const mockedFetchUserById = vi.mocked(fetchUserById)
const mockedUpdateUser = vi.mocked(updateUser)

function mountModal(props: Partial<InstanceType<typeof AdminUserFormModal>['$props']> = {}) {
  return mount(AdminUserFormModal, {
    props: {
      isOpen: true,
      userId: '',
      ...props,
    },
  })
}

async function fillCreateForm(wrapper: ReturnType<typeof mountModal>) {
  await wrapper.get('#admin-user-name').setValue('  Ana Gomez  ')
  await wrapper.get('#admin-user-email').setValue('  ana@example.com  ')
  await wrapper.get('#admin-user-password').setValue('secret')
  await wrapper.get('#admin-user-role').setValue('organizer')
  await wrapper.get('#admin-user-status').setValue('false')
}

describe('AdminUserFormModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('validates required create fields before saving', async () => {
    const wrapper = mountModal()

    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('El correo es obligatorio.')
    expect(mockedCreateUser).not.toHaveBeenCalled()
  })

  it('creates a user with the form payload and closes on success', async () => {
    mockedCreateUser.mockResolvedValue({
      id: 'user-1',
      email: 'ana@example.com',
      name: 'Ana Gomez',
      role: 'organizer',
      is_active: false,
      created_at: '2026-01-01T00:00:00Z',
    })

    const wrapper = mountModal()

    await fillCreateForm(wrapper)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(mockedCreateUser).toHaveBeenCalledWith({
      email: 'ana@example.com',
      name: 'Ana Gomez',
      is_active: false,
      password: 'secret',
      role: 'organizer',
    })
    expect(wrapper.emitted('saved')).toHaveLength(1)
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('loads an existing user when opening in edit mode', async () => {
    mockedFetchUserById.mockResolvedValue({
      id: 'user-1',
      email: 'ana@example.com',
      name: 'Ana Gomez',
      role: 'admin',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
    })

    const wrapper = mountModal({ isOpen: false, userId: 'user-1' })

    await wrapper.setProps({ isOpen: true })
    await flushPromises()

    expect(mockedFetchUserById).toHaveBeenCalledWith('user-1')
    expect((wrapper.get('#admin-user-email').element as HTMLInputElement).value).toBe(
      'ana@example.com',
    )
    expect((wrapper.get('#admin-user-role').element as HTMLSelectElement).value).toBe('admin')
  })

  it('updates an existing user without sending an empty password', async () => {
    mockedFetchUserById.mockResolvedValue({
      id: 'user-1',
      email: 'ana@example.com',
      name: 'Ana Gomez',
      role: 'attendee',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
    })
    mockedUpdateUser.mockResolvedValue({
      id: 'user-1',
      email: 'ana.nueva@example.com',
      name: 'Ana Nueva',
      role: 'admin',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
    })

    const wrapper = mountModal({ isOpen: false, userId: 'user-1' })

    await wrapper.setProps({ isOpen: true })
    await flushPromises()
    await wrapper.get('#admin-user-name').setValue('Ana Nueva')
    await wrapper.get('#admin-user-email').setValue('ana.nueva@example.com')
    await wrapper.get('#admin-user-role').setValue('admin')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(mockedUpdateUser).toHaveBeenCalledWith('user-1', {
      email: 'ana.nueva@example.com',
      name: 'Ana Nueva',
      is_active: true,
      role: 'admin',
    })
  })

  it('shows API errors when saving fails', async () => {
    mockedCreateUser.mockRejectedValue(new Error('El correo ya existe.'))

    const wrapper = mountModal()

    await fillCreateForm(wrapper)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('El correo ya existe.')
    expect(wrapper.emitted('saved')).toBeUndefined()
  })
})

