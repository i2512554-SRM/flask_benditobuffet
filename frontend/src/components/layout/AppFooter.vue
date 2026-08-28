<template>
  <footer class="app-footer">
    <div class="footer-content">
      <span class="footer-text">Bendito Buffet &copy; {{ year }}</span>
      <span class="footer-separator">&middot;</span>
      <span class="footer-text">Sistema de Gestion</span>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  padding: 0.75rem 1.5rem;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.footer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.footer-text {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.footer-separator {
  color: var(--text-muted);
  opacity: 0.4;
}
</style>
