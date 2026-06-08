<script setup lang="ts">
type InputType = 'email' | 'number' | 'password' | 'search' | 'tel' | 'text' | 'url'

const props = withDefaults(
  defineProps<{
    modelValue?: string
    id?: string
    type?: InputType
    placeholder?: string
    invalid?: boolean
    disabled?: boolean
  }>(),
  {
    modelValue: '',
    id: undefined,
    type: 'text',
    placeholder: '',
    invalid: false,
    disabled: false,
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
    :placeholder="props.placeholder"
    :type="props.type"
    :value="props.modelValue"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
