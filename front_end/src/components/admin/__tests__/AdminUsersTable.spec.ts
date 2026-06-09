import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AdminUsersTable from '../AdminUsersTable.vue'
import type { UserDTO } from '@/types/users'

const users: UserDTO[] = [
  {
    id: 'user-1',
    email: 'ana@example.com',
    name: 'Ana Gomez',
    role: 'admin',
    is_active: true,
    created_at: '2026-01-05T12:00:00Z',
  },
  {
    id: 'user-2',
    email: 'lu@example.com',
    name: 'Lu',
    role: 'attendee',
    is_active: false,
    created_at: '2026-01-06T12:00:00Z',
  },
]

describe('AdminUsersTable', () => {
  it('renders user labels, initials and statuses', () => {
    const wrapper = mount(AdminUsersTable, {
      props: {
        deletingUserId: '',
        users,
      },
    })

    expect(wrapper.text()).toContain('Ana Gomez')
    expect(wrapper.text()).toContain('AG')
    expect(wrapper.text()).toContain('Admin')
    expect(wrapper.text()).toContain('Activo')
    expect(wrapper.text()).toContain('LU')
    expect(wrapper.text()).toContain('Inactivo')
  })

  it('emits edit and delete actions for active users', async () => {
    const wrapper = mount(AdminUsersTable, {
      props: {
        deletingUserId: '',
        users,
      },
    })

    const buttons = wrapper.findAll('button')

    await buttons[0]!.trigger('click')
    await buttons[1]!.trigger('click')

    expect(wrapper.emitted('edit')).toEqual([['user-1']])
    expect(wrapper.emitted('delete')).toEqual([[users[0]]])
  })

  it('disables delete for inactive users and users being deleted', () => {
    const wrapper = mount(AdminUsersTable, {
      props: {
        deletingUserId: 'user-1',
        users,
      },
    })

    const deleteButtons = wrapper.findAll('button').filter((button) => button.text().includes('Desactivar'))

    expect(deleteButtons[0]!.attributes('disabled')).toBeDefined()
    expect(deleteButtons[1]!.attributes('disabled')).toBeDefined()
  })
})
