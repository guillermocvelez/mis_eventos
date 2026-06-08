<script setup lang="ts">
import { UiIcon } from '@/components/ui'
</script>

<template>
  <section class="events-empty" aria-live="polite">
    <div class="empty-icon">
      <UiIcon name="ticket" :size="28" />
    </div>
    <h2>Cargando eventos</h2>
    <p>Estamos consultando los eventos disponibles.</p>
  </section>
</template>
