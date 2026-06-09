<script setup lang="ts">
import { onBeforeUnmount, watch } from 'vue'

import UiIcon from './UiIcon.vue'

type ToastVariant = 'success' | 'danger' | 'info'

const props = withDefaults(
  defineProps<{
    duration?: number
    message?: string
    open?: boolean
    variant?: ToastVariant
  }>(),
  {
    duration: 4000,
    message: '',
    open: false,
    variant: 'info',
  },
)

const emit = defineEmits<{
  close: []
}>()

let closeTimer: number | undefined

watch(
  () => [props.open, props.message, props.duration] as const,
  ([isOpen, message, duration]) => {
    clearCloseTimer()

    if (isOpen && message && duration > 0) {
      closeTimer = window.setTimeout(() => {
        emit('close')
      }, duration)
    }
  },
  { immediate: true },
)

onBeforeUnmount(clearCloseTimer)

function clearCloseTimer() {
  if (!closeTimer) return

  window.clearTimeout(closeTimer)
  closeTimer = undefined
}
</script>

<template>
  <Transition name="toast">
    <div v-if="open && message" class="toast" :class="`toast-${variant}`" role="status">
      <p>{{ message }}</p>
      <button
        class="toast-close"
        type="button"
        aria-label="Cerrar notificación"
        @click="emit('close')"
      >
        <UiIcon name="x" :size="16" />
      </button>
    </div>
  </Transition>
</template>
