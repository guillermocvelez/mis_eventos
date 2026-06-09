<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { UiButton, UiField, UiIcon, UiModal, UiTextInput } from '@/components/ui'
import { createUser, fetchUserById, updateUser } from '@/services/usersApi'
import type { UserCreatePayload, UserRole, UserUpdatePayload } from '@/types/users'

type UserFormState = {
  email: string
  name: string
  isActive: 'false' | 'true'
  password: string
  role: UserRole
}

const props = defineProps<{
  isOpen: boolean
  userId: string
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const isSaving = ref(false)
const formError = ref('')
const form = reactive<UserFormState>({
  email: '',
  name: '',
  isActive: 'true',
  password: '',
  role: 'attendee',
})

const isEditing = computed(() => Boolean(props.userId))
const formTitle = computed(() => (isEditing.value ? 'Editar usuario' : 'Crear usuario'))
const formActionLabel = computed(() => (isEditing.value ? 'Guardar cambios' : 'Crear usuario'))

watch(
  [() => props.isOpen, () => props.userId],
  ([open, id]) => {
    if (!open) {
      resetForm()
      return
    }

    formError.value = ''

    if (id) {
      void loadUserForEdit(id)
    } else {
      resetForm()
    }
  },
)

function resetForm() {
  form.email = ''
  form.name = ''
  form.password = ''
  form.role = 'attendee'
  form.isActive = 'true'
  formError.value = ''
  isSaving.value = false
}

async function loadUserForEdit(id: string) {
  try {
    const user = await fetchUserById(id)
    form.email = user.email
    form.name = user.name
    form.password = ''
    form.role = user.role
    form.isActive = user.is_active ? 'true' : 'false'
  } catch (caughtError) {
    emit('close')
    // Surface the error to the parent via a re-throw so the view can show a toast
    throw caughtError
  }
}

async function submitForm() {
  formError.value = ''

  if (!form.email.trim()) {
    formError.value = 'El correo es obligatorio.'
    return
  }

  if (!isEditing.value && !form.password.trim()) {
    formError.value = 'La contraseña es obligatoria para crear usuarios.'
    return
  }

  isSaving.value = true

  try {
    if (isEditing.value) {
      const payload: UserUpdatePayload = {
        email: form.email.trim(),
        name: form.name.trim(),
        is_active: form.isActive === 'true',
        role: form.role,
      }

      if (form.password.trim()) {
        payload.password = form.password
      }

      await updateUser(props.userId, payload)
    } else {
      const payload: UserCreatePayload = {
        email: form.email.trim(),
        name: form.name.trim(),
        is_active: form.isActive === 'true',
        password: form.password,
        role: form.role,
      }

      await createUser(payload)
    }

    emit('saved')
    emit('close')
  } catch (caughtError) {
    formError.value =
      caughtError instanceof Error
        ? caughtError.message
        : 'No pudimos guardar el usuario. Inténtalo de nuevo.'
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <UiModal :open="isOpen">
    <form class="admin-user-form" @submit.prevent="submitForm">
      <div class="card-header">
        <div>
          <h2 class="card-title">{{ formTitle }}</h2>
          <p class="card-description">
            {{ isEditing ? 'Actualiza los datos del usuario.' : 'Crea una cuenta administrada.' }}
          </p>
        </div>
        <button class="icon-btn light" type="button" aria-label="Cerrar" @click="emit('close')">
          <UiIcon name="x" :size="18" />
        </button>
      </div>

      <div class="admin-user-form-body">
        <p v-if="formError" class="form-alert">{{ formError }}</p>

        <UiField for-id="admin-user-name" label="Nombre">
          <UiTextInput
            id="admin-user-name"
            v-model="form.name"
            placeholder="Nombre de usuario"
            type="text"
          />
        </UiField>

        <UiField for-id="admin-user-email" label="Correo">
          <UiTextInput
            id="admin-user-email"
            v-model="form.email"
            placeholder="usuario@empresa.com"
            type="email"
          />
        </UiField>

        <UiField
          for-id="admin-user-password"
          label="Contraseña"
          :hint="isEditing ? 'Déjala vacía si no quieres cambiarla.' : ''"
        >
          <UiTextInput
            id="admin-user-password"
            v-model="form.password"
            :placeholder="isEditing ? 'Sin cambios' : 'Contraseña inicial'"
            type="password"
          />
        </UiField>

        <div class="admin-form-grid">
          <UiField for-id="admin-user-role" label="Rol">
            <select id="admin-user-role" v-model="form.role" class="input">
              <option value="attendee">Asistente</option>
              <option value="organizer">Organizador</option>
              <option value="admin">Admin</option>
            </select>
          </UiField>

          <UiField for-id="admin-user-status" label="Estado">
            <select id="admin-user-status" v-model="form.isActive" class="input">
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </select>
          </UiField>
        </div>
      </div>

      <div class="card-footer form-actions">
        <UiButton :disabled="isSaving" type="button" variant="ghost" @click="emit('close')">
          Cancelar
        </UiButton>
        <UiButton :disabled="isSaving" type="submit">
          {{ isSaving ? 'Guardando...' : formActionLabel }}
        </UiButton>
      </div>
    </form>
  </UiModal>
</template>
