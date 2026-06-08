<script setup lang="ts">
import { RouterLink } from 'vue-router'

import { UiSegment } from '@/components/ui'

defineProps<{
  mode: 'login' | 'register'
}>()
</script>

<template>
  <main class="auth-layout">
    <section class="auth-card card" aria-labelledby="auth-title">
      <header class="auth-header">
        <div class="row gap-12">
          <span class="brand-mark">ME</span>
          <div>
            <h1 id="auth-title">Mis Eventos</h1>
            <p>Gestiona tus eventos con inteligencia</p>
          </div>
        </div>
      </header>

      <UiSegment>
        <RouterLink class="segment-option" :class="{ on: mode === 'login' }" to="/login">
          Iniciar sesión
        </RouterLink>
        <RouterLink class="segment-option" :class="{ on: mode === 'register' }" to="/registro">
          Crear cuenta
        </RouterLink>
      </UiSegment>

      <slot />
    </section>
  </main>
</template>
