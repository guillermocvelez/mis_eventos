import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/eventos',
    },
    {
      path: '/eventos',
      name: 'events-home',
      component: () => import('@/views/events/EventsHomeView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/eventos/crear',
      name: 'event-create',
      component: () => import('@/views/events/EventCreateView.vue'),
      meta: {
        requiresAuth: true,
        requiresManageEvents: true,
      },
    },
    {
      path: '/eventos/:eventId/editar',
      name: 'event-edit',
      component: () => import('@/views/events/EventEditView.vue'),
      meta: {
        requiresAuth: true,
        requiresManageEvents: true,
      },
    },
    {
      path: '/eventos/:eventId',
      name: 'event-detail',
      component: () => import('@/views/events/EventDetailView.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: {
        guestOnly: true,
      },
    },
    {
      path: '/registro',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: {
        guestOnly: true,
      },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (authStore.isTokenExpired) {
    authStore.logout()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (to.meta.requiresManageEvents && !authStore.canManageEvents) {
    return '/eventos'
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return '/eventos'
  }
})

export default router
