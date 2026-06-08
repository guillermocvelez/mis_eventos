<script setup lang="ts">
defineProps<{
  label?: string
  hint?: string
  error?: string
  forId?: string
}>()
</script>

<template>
  <div class="field">
    <div v-if="label || $slots.action" class="field-label-row">
      <label v-if="label" class="field-label" :for="forId">{{ label }}</label>
      <slot name="action" />
    </div>
    <slot />
    <p v-if="error" class="field-error">{{ error }}</p>
    <p v-else-if="hint" class="field-hint">{{ hint }}</p>
  </div>
</template>
