<script setup lang="ts">
type InputType =
  | 'date'
  | 'datetime-local'
  | 'email'
  | 'number'
  | 'password'
  | 'search'
  | 'tel'
  | 'text'
  | 'time'
  | 'url'

const props = withDefaults(
  defineProps<{
    modelValue?: string
    id?: string
    type?: InputType
    placeholder?: string
    invalid?: boolean
    disabled?: boolean
    min?: string
  }>(),
  {
    modelValue: '',
    id: undefined,
    type: 'text',
    placeholder: '',
    invalid: false,
    disabled: false,
    min: undefined,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <input
    class="input"
    :aria-invalid="props.invalid || undefined"
    :disabled="props.disabled"
    :id="props.id"
    :min="props.min"
    :placeholder="props.placeholder"
    :type="props.type"
    :value="props.modelValue"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
