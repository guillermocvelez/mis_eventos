<script setup lang="ts">
import { computed, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import EventsSidebar from '@/components/events/EventsSidebar.vue'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'

const authStore = useAuthStore()
const eventsStore = useEventsStore()
const route = useRoute()

const showSidebar = computed(() => route.meta.requiresAuth === true)
const eventCount = computed(() => eventsStore.total)

watch(
  showSidebar,
  async (isVisible) => {
    if (isVisible && authStore.isAuthenticated && eventsStore.total === 0 && !eventsStore.isLoading) {
      await eventsStore.fetchEvents({ limit: 1, page: 1 })
    }
  },
  { immediate: true },
)
</script>

<template>
  <div v-if="showSidebar" class="app-shell app-shell--auth">
    <EventsSidebar :event-count="eventCount" />

    <div class="app-shell__content">
      <RouterView />
    </div>
  </div>

  <RouterView v-else />
</template>
