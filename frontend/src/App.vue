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
  return state.initialized && isAuthenticated.value && route.name !== 'Auth'
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
}

.app-page {
  flex: 1;
  min-width: 0;
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
