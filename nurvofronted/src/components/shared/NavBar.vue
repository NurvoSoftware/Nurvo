<script setup lang="ts">
defineProps<{
  step?: number
  stepLabel?: string
}>()
</script>

<template>
  <nav class="topbar">
    <div class="brand">
      <div class="brand-logo">N</div>
      <span class="brand-name">Nurvo</span>
    </div>
  </nav>
</template>

<style scoped>
.topbar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 6px 20px 26px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--nurvo-gradient-logo);
  color: var(--nurvo-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 800;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.28);
}

.brand-name {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--nurvo-text-primary);
}

@media (max-width: 768px) {
  .topbar {
    padding: 6px 16px 20px;
  }
}
</style>
