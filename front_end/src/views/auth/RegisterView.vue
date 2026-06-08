<script setup lang="ts">
import { RouterLink } from 'vue-router'

import AuthShell from '@/components/auth/AuthShell.vue'
import PasswordInput from '@/components/auth/PasswordInput.vue'
import { UiButton, UiField, UiIcon, UiTextInput } from '@/components/ui'
</script>

<template>
  <AuthShell mode="register">
    <form class="auth-form col gap-16" novalidate>
      <UiField for-id="name" label="Nombre completo">
        <div class="input-shell">
          <span class="input-icon lead">
            <UiIcon name="user" />
          </span>
          <UiTextInput id="name" autocomplete="name" class="has-lead" />
        </div>
      </UiField>

      <UiField for-id="email" label="Correo electrónico">
        <div class="input-shell">
          <span class="input-icon lead">
            <UiIcon name="mail" />
          </span>
          <UiTextInput id="email" autocomplete="email" class="has-lead" type="email" />
        </div>
      </UiField>

      <UiField
        for-id="password"
        hint="Mínimo 8 caracteres, una mayúscula y un número."
        label="Contraseña"
      >
        <PasswordInput id="password" autocomplete="new-password" />
      </UiField>

      <UiButton block size="lg" type="button">Crear cuenta</UiButton>
    </form>

    <p class="auth-footer muted">
      ¿Ya tienes cuenta?
      <RouterLink to="/login">Inicia sesión</RouterLink>
    </p>
  </AuthShell>
</template>
