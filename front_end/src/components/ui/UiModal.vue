<script setup lang="ts">
withDefaults(
  defineProps<{
    open?: boolean
  }>(),
  {
    open: false,
  },
)
</script>

<template>
  <div v-if="open" class="modal-overlay">
    <section class="modal" role="dialog" aria-modal="true">
      <slot />
    </section>
  </div>
</template>
