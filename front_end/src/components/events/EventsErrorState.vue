<script setup lang="ts">
import { UiButton, UiIcon } from '@/components/ui'

defineProps<{
  message: string
}>()

const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <section class="events-empty" aria-live="polite">
    <div class="empty-icon danger">
      <UiIcon name="ticket" :size="28" />
    </div>
    <h2>No pudimos cargar los eventos</h2>
    <p>{{ message }}</p>
    <UiButton variant="secondary" @click="emit('retry')"> Reintentar </UiButton>
  </section>
</template>
