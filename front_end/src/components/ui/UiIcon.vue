<script setup lang="ts">
type IconName =
  | 'calendar'
  | 'circle-plus'
  | 'eye'
  | 'eye-off'
  | 'home'
  | 'lock'
  | 'log-out'
  | 'mail'
  | 'map-pin'
  | 'plus'
  | 'search'
  | 'shield'
  | 'ticket'
  | 'user'
  | 'users'

withDefaults(
  defineProps<{
    name: IconName
    size?: number
  }>(),
  {
    size: 18,
  },
)

const paths: Record<IconName, string> = {
  calendar: '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18M8 2v4M16 2v4"/>',
  'circle-plus': '<circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/>',
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
  'eye-off':
    '<path d="M10.7 5.1A9.9 9.9 0 0 1 12 5c6.5 0 10 7 10 7a13.2 13.2 0 0 1-1.7 2.7M6.6 6.6A13.4 13.4 0 0 0 2 12s3.5 7 10 7a9.8 9.8 0 0 0 5.4-1.6M14.1 14.1a3 3 0 0 1-4.2-4.2"/><path d="M2 2l20 20"/>',
  home: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/><path d="M9 22V12h6v10"/>',
  lock: '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  'log-out': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
  mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
  'map-pin':
    '<path d="M20 10c0 4.4-8 12-8 12s-8-7.6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
  plus: '<path d="M5 12h14M12 5v14"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  shield: '<path d="M20 13c0 5-3.5 7.5-7.3 8.8a2 2 0 0 1-1.4 0C7.5 20.5 4 18 4 13V6a2 2 0 0 1 1.2-1.8l6-2.7a2 2 0 0 1 1.6 0l6 2.7A2 2 0 0 1 20 6Z"/>',
  ticket:
    '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v14"/>',
  user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  users:
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
}
</script>

<template>
  <svg
    aria-hidden="true"
    fill="none"
    :height="size"
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width="2"
    viewBox="0 0 24 24"
    :width="size"
    v-html="paths[name]"
  />
</template>
