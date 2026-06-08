<script setup lang="ts">
import { UiButton, UiIcon } from '@/components/ui'

const emit = defineEmits<{
  'clear-search': []
}>()
</script>

<template>
  <section class="events-empty" aria-live="polite">
    <div class="empty-icon">
      <UiIcon name="search" :size="28" />
    </div>
    <h2>No encontramos eventos con ese nombre</h2>
    <p>Prueba con otras palabras clave o limpia los filtros para ver todos los eventos disponibles.</p>
    <UiButton variant="secondary" @click="emit('clear-search')">Limpiar búsqueda</UiButton>
  </section>
</template>
