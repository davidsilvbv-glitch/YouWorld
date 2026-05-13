<template>
  <div class="app-frame" :class="{ 'has-sidebar': showSidebar }">
    <ProjectSidebar v-if="showSidebar" />
    <main class="app-page">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ProjectSidebar from './components/ProjectSidebar.vue'
import { initializeAuthSession, useAuthSession } from './store/authSession'

const route = useRoute()
const { state, isAuthenticated } = useAuthSession()

const showSidebar = computed(() => {
  return state.initialized && isAuthenticated.value && route.name !== 'Auth' && route.name !== 'Home'
})

onMounted(() => {
  initializeAuthSession()
})
</script>

<style>
/* Reset global de estilos */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

.app-frame {
  min-height: 100vh;
  display: flex;
  background:
    radial-gradient(circle at 68% 14%, rgba(77, 203, 190, 0.14), transparent 28%),
    radial-gradient(circle at 24% 12%, rgba(86, 36, 126, 0.18), transparent 26%),
    linear-gradient(125deg, #050607 0%, #09120f 35%, #0b0715 72%, #05020a 100%);
}

.app-page {
  flex: 1;
  min-width: 0;
  position: relative;
}

.app-page::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 44px;
  pointer-events: none;
  background: linear-gradient(90deg, rgba(10, 10, 18, 0.16), transparent 78%);
  opacity: 0.7;
}

/* Estilos de barra de desplazamiento */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

/* Estilos de botón global */
button {
  font-family: inherit;
}

@media (max-width: 1100px) {
  .app-frame {
    display: block;
  }
}
</style>
