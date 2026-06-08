<template>
  <div class="app-shell">
    <aside class="sidebar">
      <slot name="sidebar" />
    </aside>

    <main class="page">
      <header class="topbar">
        <div>
          <slot name="title" />
        </div>
        <div v-if="$slots.actions">
          <slot name="actions" />
        </div>
      </header>

      <div class="page-content">
        <slot />
      </div>
    </main>
  </div>
</template>
