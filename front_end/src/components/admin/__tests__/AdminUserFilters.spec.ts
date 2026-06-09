import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AdminUserFilters from '../AdminUserFilters.vue'

describe('AdminUserFilters', () => {
  it('emits model updates for search, role and status filters', async () => {
    const wrapper = mount(AdminUserFilters, {
      props: {
        searchQuery: '',
        roleFilter: 'all',
        statusFilter: 'all',
      },
    })

    await wrapper.get('input').setValue('ana@example.com')
    const selects = wrapper.findAll('select')

    await selects[0]!.setValue('admin')
    await selects[1]!.setValue('inactive')

    expect(wrapper.emitted('update:searchQuery')?.[0]).toEqual(['ana@example.com'])
    expect(wrapper.emitted('update:roleFilter')?.[0]).toEqual(['admin'])
    expect(wrapper.emitted('update:statusFilter')?.[0]).toEqual(['inactive'])
  })
})
