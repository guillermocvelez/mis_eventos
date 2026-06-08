<template>
  <article class="card">
    <header
      v-if="$slots.header || $slots.title || $slots.description || $slots.actions"
      class="card-header"
    >
      <slot name="header">
        <div>
          <h2 v-if="$slots.title" class="card-title">
            <slot name="title" />
          </h2>
          <p v-if="$slots.description" class="card-description">
            <slot name="description" />
          </p>
        </div>
        <div v-if="$slots.actions">
          <slot name="actions" />
        </div>
      </slot>
    </header>

    <div class="card-body">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </footer>
  </article>
</template>
