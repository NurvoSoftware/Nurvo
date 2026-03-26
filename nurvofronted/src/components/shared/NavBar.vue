<script setup lang="ts">
defineProps<{
  step?: number
  stepLabel?: string
}>()
</script>

<template>
  <nav class="nurvo-nav">
    <div class="nurvo-nav-logo">
      <div class="nurvo-nav-logo-icon">N</div>
      <span class="nurvo-nav-logo-text">Nurvo</span>
    </div>
    <div v-if="step" class="nurvo-nav-step">
      Step {{ step }} of 3<template v-if="stepLabel"> - {{ stepLabel }}</template>
    </div>
  </nav>
</template>
