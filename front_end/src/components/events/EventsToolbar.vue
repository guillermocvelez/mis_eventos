<script setup lang="ts">
import { UiIcon, UiTextInput } from '@/components/ui'

defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <section class="events-toolbar" aria-label="Filtros de eventos">
    <div class="searchbar">
      <span class="input-icon lead">
        <UiIcon name="search" />
      </span>
      <UiTextInput
        class="has-lead"
        :model-value="modelValue"
        placeholder="Buscar eventos"
        type="search"
        @update:model-value="emit('update:modelValue', $event)"
      />
    </div>
  </section>
</template>
