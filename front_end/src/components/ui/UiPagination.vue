<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage: number
  totalPages: number
  totalItems: number
  itemsShown: number
}>()

const emit = defineEmits<{
  'page-change': [page: number]
}>()

const pageButtons = computed(() => {
  const safePages = Math.max(props.totalPages, 1)
  const start = Math.max(Math.min(props.currentPage - 2, safePages - 4), 1)
  const end = Math.min(start + 4, safePages)

  return Array.from({ length: end - start + 1 }, (_, index) => start + index)
})

function goToPage(page: number) {
  if (page < 1 || page > props.totalPages || page === props.currentPage) return

  emit('page-change', page)
}
</script>

<template>
  <footer class="admin-pagination">
    <p>Mostrando {{ itemsShown }} de {{ totalItems }} usuarios</p>

    <nav aria-label="Paginación" class="admin-page-list">
      <button type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
        ‹
      </button>
      <button
        v-for="page in pageButtons"
        :key="page"
        :class="{ active: page === currentPage }"
        type="button"
        @click="goToPage(page)"
      >
        {{ page }}
      </button>
      <button
        type="button"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        ›
      </button>
    </nav>
  </footer>
</template>
