<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordInput from '@/components/auth/PasswordInput.vue'
import { UiButton, UiField, UiIcon, UiTextInput } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const submitted = ref(false)

const nameError = computed(() => {
  if (!submitted.value) return ''
  return name.value.trim().length >= 2 ? '' : 'Escribe tu nombre completo.'
})

const emailError = computed(() => {
  if (!submitted.value) return ''
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
    ? ''
    : 'Introduce un correo electrónico válido.'
})

const passwordError = computed(() => {
  if (!submitted.value) return ''
  return password.value.length >= 8 ? '' : 'La contraseña debe tener al menos 8 caracteres.'
})

const hasValidationErrors = computed(
  () => Boolean(nameError.value || emailError.value || passwordError.value),
)

async function submitRegister() {
  submitted.value = true

  if (hasValidationErrors.value) return

  try {
    await authStore.register({
      name: name.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    await router.push('/eventos')
  } catch {
    // The store owns the visible error message.
  }
}
</script>

<template>
  <AuthShell mode="register">
    <form class="auth-form col gap-16" novalidate @submit.prevent="submitRegister">
      <UiField for-id="name" :error="nameError" label="Nombre completo">
        <div class="input-shell">
          <span class="input-icon lead">
            <UiIcon name="user" />
          </span>
          <UiTextInput
            id="name"
            v-model="name"
            autocomplete="name"
            class="has-lead"
            :invalid="Boolean(nameError)"
          />
        </div>
      </UiField>

      <UiField for-id="email" :error="emailError" label="Correo electrónico">
        <div class="input-shell">
          <span class="input-icon lead">
            <UiIcon name="mail" />
          </span>
          <UiTextInput
            id="email"
            v-model="email"
            autocomplete="email"
            class="has-lead"
            :invalid="Boolean(emailError)"
            type="email"
          />
        </div>
      </UiField>

      <UiField
        :error="passwordError"
        for-id="password"
        hint="Mínimo 8 caracteres, una mayúscula y un número."
        label="Contraseña"
      >
        <PasswordInput
          id="password"
          v-model="password"
          autocomplete="new-password"
          :invalid="Boolean(passwordError)"
        />
      </UiField>

      <p v-if="authStore.error" class="auth-alert auth-alert-error" role="alert">
        {{ authStore.error }}
      </p>

      <UiButton block :disabled="authStore.isLoading" size="lg" type="submit">
        {{ authStore.isLoading ? 'Creando cuenta...' : 'Crear cuenta' }}
      </UiButton>
    </form>

    <p class="auth-footer muted">
      ¿Ya tienes cuenta?
      <RouterLink to="/login">Inicia sesión</RouterLink>
    </p>
  </AuthShell>
</template>
