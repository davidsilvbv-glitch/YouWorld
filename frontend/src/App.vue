<template>
  <div class="app-frame" :class="{ 'has-sidebar': showSidebar, 'sidebar-collapsed': showSidebar && isSidebarCollapsed }">
    <div v-if="showSidebar" class="sidebar-shell" :class="{ collapsed: isSidebarCollapsed }">
      <button
        class="sidebar-toggle"
        :class="{ collapsed: isSidebarCollapsed }"
        @click="toggleSidebar"
        :aria-label="isSidebarCollapsed ? 'Mostrar proyectos' : 'Ocultar proyectos'"
      >
        <span class="sidebar-toggle-icon">{{ isSidebarCollapsed ? '›' : '‹' }}</span>
      </button>
      <ProjectSidebar />
    </div>
    <main class="app-page">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ProjectSidebar from './components/ProjectSidebar.vue'
import { initializeAuthSession, useAuthSession } from './store/authSession'

const route = useRoute()
const { state, isAuthenticated } = useAuthSession()
const isSidebarCollapsed = ref(true)

const showSidebar = computed(() => {
  return state.initialized && isAuthenticated.value && route.name !== 'Auth' && route.name !== 'Home'
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

watch(
  () => route.name,
  (name) => {
    if (name && name !== 'Home' && name !== 'Auth') {
      isSidebarCollapsed.value = true
    }
  },
  { immediate: true }
)

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
  align-items: stretch;
  background:
    radial-gradient(circle at 68% 14%, rgba(77, 203, 190, 0.14), transparent 28%),
    radial-gradient(circle at 24% 12%, rgba(86, 36, 126, 0.18), transparent 26%),
    linear-gradient(125deg, #050607 0%, #09120f 35%, #0b0715 72%, #05020a 100%);
}

.sidebar-shell {
  position: relative;
  width: 278px;
  min-width: 278px;
  transition: width 0.28s ease, min-width 0.28s ease;
}

.sidebar-shell.collapsed {
  width: 28px;
  min-width: 28px;
  overflow: visible;
}

.sidebar-shell :deep(.project-sidebar) {
  transition: transform 0.28s ease, opacity 0.22s ease;
}

.sidebar-shell.collapsed :deep(.project-sidebar) {
  transform: translateX(calc(-100% + 18px));
  opacity: 0;
  pointer-events: none;
}

.sidebar-toggle {
  position: absolute;
  top: 96px;
  right: -12px;
  z-index: 30;
  width: 32px;
  height: 68px;
  border: 0;
  border-radius: 0 18px 18px 0;
  background: linear-gradient(180deg, rgba(18, 21, 31, 0.96), rgba(12, 16, 24, 0.92));
  color: rgba(212, 236, 232, 0.82);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22), inset 0 0 0 1px rgba(118, 163, 157, 0.16);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: background 0.2s ease, color 0.2s ease, right 0.28s ease, transform 0.2s ease;
}

.sidebar-toggle:hover {
  background: linear-gradient(180deg, rgba(28, 37, 49, 0.98), rgba(16, 23, 34, 0.96));
  color: #eefaf7;
  transform: translateX(1px);
}

.sidebar-toggle.collapsed {
  right: -12px;
}

.sidebar-toggle-icon {
  font-size: 1.4rem;
  line-height: 1;
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

  .sidebar-shell {
    display: none;
  }
}
</style>
