<script setup lang="ts">
type BadgeVariant = 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'purple'

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariant
  }>(),
  {
    variant: 'neutral',
  },
)
</script>

<template>
  <span class="badge" :class="props.variant !== 'neutral' && `badge-${props.variant}`">
    <slot />
  </span>
</template>
