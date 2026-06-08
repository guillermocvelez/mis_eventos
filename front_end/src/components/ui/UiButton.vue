<script setup lang="ts">
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
type ButtonSize = 'sm' | 'md' | 'lg'
type ButtonType = 'button' | 'submit' | 'reset'

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant
    size?: ButtonSize
    block?: boolean
    disabled?: boolean
    type?: ButtonType
  }>(),
  {
    variant: 'primary',
    size: 'md',
    block: false,
    disabled: false,
    type: 'button',
  },
)
</script>

<template>
  <button
    class="btn"
    :class="[
      `btn-${props.variant}`,
      props.size !== 'md' && `btn-${props.size}`,
      props.block && 'btn-block',
    ]"
    :disabled="props.disabled"
    :type="props.type"
  >
    <slot />
  </button>
</template>
