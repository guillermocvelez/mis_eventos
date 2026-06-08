<script setup lang="ts">
import { ref } from 'vue'

import { UiIcon, UiTextInput } from '@/components/ui'

withDefaults(
  defineProps<{
    autocomplete?: string
    id: string
    invalid?: boolean
    modelValue?: string
    placeholder?: string
  }>(),
  {
    autocomplete: undefined,
    invalid: false,
    modelValue: '',
    placeholder: '',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const visible = ref(false)
</script>

<template>
  <div class="input-shell">
    <span class="input-icon lead">
      <UiIcon name="lock" />
    </span>
    <UiTextInput
      class="has-lead has-trail"
      :autocomplete="autocomplete"
      :id="id"
      :invalid="invalid"
      :model-value="modelValue"
      :placeholder="placeholder"
      :type="visible ? 'text' : 'password'"
      @update:model-value="emit('update:modelValue', $event)"
    />
    <button
      class="trail trail-button"
      type="button"
      :aria-label="visible ? 'Ocultar contraseña' : 'Mostrar contraseña'"
      @click="visible = !visible"
    >
      <UiIcon :name="visible ? 'eye-off' : 'eye'" />
    </button>
  </div>
</template>
