<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordInput from '@/components/auth/PasswordInput.vue'
import { UiButton, UiField, UiIcon, UiTextInput } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const submitted = ref(false)

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

const hasValidationErrors = computed(() => Boolean(emailError.value || passwordError.value))

async function submitLogin() {
  submitted.value = true

  if (hasValidationErrors.value) return

  try {
    await authStore.login({
      email: email.value,
      password: password.value,
    })
    await router.push(typeof route.query.redirect === 'string' ? route.query.redirect : '/eventos')
  } catch {
    // The store owns the visible error message.
  }
}
</script>

<template>
  <AuthShell mode="login">
    <form class="auth-form col gap-16" novalidate @submit.prevent="submitLogin">
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

      <UiField for-id="password" :error="passwordError" label="Contraseña">
        <template #action>
          <RouterLink class="auth-inline-link" to="/recuperar-contrasena">
            ¿Olvidaste tu contraseña?
          </RouterLink>
        </template>
        <PasswordInput
          id="password"
          v-model="password"
          autocomplete="current-password"
          :invalid="Boolean(passwordError)"
        />
      </UiField>

      <p v-if="authStore.error" class="auth-alert auth-alert-error" role="alert">
        {{ authStore.error }}
      </p>

      <UiButton block :disabled="authStore.isLoading" size="lg" type="submit">
        {{ authStore.isLoading ? 'Iniciando sesión...' : 'Iniciar sesión' }}
      </UiButton>
    </form>

    <p class="auth-footer muted">
      ¿No tienes cuenta?
      <RouterLink to="/registro">Regístrate gratis</RouterLink>
    </p>
  </AuthShell>
</template>
