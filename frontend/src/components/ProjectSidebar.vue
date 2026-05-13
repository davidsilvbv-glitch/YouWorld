<template>
  <aside class="project-sidebar" :class="{ embedded }">
    <div class="sidebar-top">
      <button v-if="!embedded" class="sidebar-brand" @click="router.push('/')">YouWorld</button>
      <button class="sidebar-new-btn" @click="router.push('/')">+ Nuevo proyecto</button>
    </div>

    <div class="sidebar-section">
      <div class="sidebar-section-title">Tus proyectos</div>

      <div v-if="loading" class="sidebar-state">Cargando proyectos...</div>
      <div v-else-if="projects.length === 0" class="sidebar-state">
        Cuando crees un mundo aparecerá aquí.
      </div>
      <div v-else class="sidebar-list">
        <button
          v-for="project in projects"
          :key="project.project_id"
          class="sidebar-item"
          :class="{ active: activeProjectId === project.project_id }"
          @click="openProject(project.project_id)"
        >
          <span class="sidebar-item-name">{{ project.name || 'Proyecto sin nombre' }}</span>
          <span class="sidebar-item-meta">
            <span class="sidebar-status" :class="statusClass(project.status)">
              {{ statusLabel(project.status) }}
            </span>
            <span>{{ formatDate(project.updated_at || project.created_at) }}</span>
          </span>
        </button>
      </div>
    </div>

    <div class="sidebar-user" v-if="state.user">
      <img
        v-if="state.user.avatar_url"
        :src="state.user.avatar_url"
        alt=""
        class="sidebar-avatar"
      />
      <div v-else class="sidebar-avatar fallback">
        {{ initials }}
      </div>
      <div class="sidebar-user-copy">
        <div class="sidebar-user-name">{{ state.user.name || 'Usuario' }}</div>
        <div class="sidebar-user-email">{{ state.user.email }}</div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listProjects } from '../api/graph'
import { useAuthSession } from '../store/authSession'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const route = useRoute()
const { state, isAuthenticated } = useAuthSession()

const loading = ref(false)
const projects = ref([])

const activeProjectId = computed(() => {
  if (route.name === 'Process') return route.params.projectId
  return null
})

const initials = computed(() => {
  const source = state.user?.name || state.user?.email || 'YW'
  return source
    .split(/\s+/)
    .slice(0, 2)
    .map(part => part.charAt(0).toUpperCase())
    .join('')
})

const formatDate = (value) => {
  if (!value) return 'Sin fecha'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-BO', {
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const statusLabel = (status) => {
  switch (status) {
    case 'created':
      return 'Borrador'
    case 'ontology_generated':
      return 'Ontología lista'
    case 'graph_building':
      return 'Construyendo'
    case 'graph_completed':
      return 'Activo'
    case 'failed':
      return 'Fallido'
    default:
      return 'Proyecto'
  }
}

const statusClass = (status) => {
  if (status === 'graph_completed') return 'is-complete'
  if (status === 'failed') return 'is-failed'
  if (status === 'graph_building') return 'is-live'
  return 'is-draft'
}

const fetchProjects = async () => {
  if (!isAuthenticated.value) {
    projects.value = []
    return
  }

  loading.value = true
  try {
    const res = await listProjects(100)
    projects.value = Array.isArray(res?.data) ? res.data : []
  } catch (error) {
    console.warn('Could not load projects:', error)
    projects.value = []
  } finally {
    loading.value = false
  }
}

const openProject = (projectId) => {
  router.push({ name: 'Process', params: { projectId } })
}

const handleProjectsChanged = () => {
  fetchProjects()
}

watch(
  () => state.user?.user_id,
  () => {
    fetchProjects()
  },
  { immediate: true }
)

watch(
  () => route.fullPath,
  () => {
    fetchProjects()
  }
)

onMounted(() => {
  window.addEventListener('focus', handleProjectsChanged)
  window.addEventListener('youworld:projects-changed', handleProjectsChanged)
})

onBeforeUnmount(() => {
  window.removeEventListener('focus', handleProjectsChanged)
  window.removeEventListener('youworld:projects-changed', handleProjectsChanged)
})
</script>

<style scoped>
.project-sidebar {
  width: 278px;
  min-width: 278px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 18px 14px 16px;
  background:
    radial-gradient(circle at 12% 10%, rgba(112, 37, 194, 0.22), transparent 30%),
    radial-gradient(circle at 85% 88%, rgba(35, 123, 110, 0.14), transparent 34%),
    linear-gradient(180deg, rgba(8, 8, 17, 0.86), rgba(8, 7, 18, 0.74));
  border-right: 0;
  box-shadow: inset -18px 0 36px rgba(18, 13, 33, 0.18);
}

.project-sidebar.embedded {
  min-height: auto;
  height: auto;
  padding: 4px 14px 16px 0;
  background: transparent;
  box-shadow: none;
}

.sidebar-top {
  display: grid;
  gap: 12px;
}

.sidebar-brand,
.sidebar-new-btn,
.sidebar-item {
  border: 0;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.sidebar-brand {
  color: rgba(245, 255, 252, 0.96);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  padding: 6px 8px;
}

.sidebar-new-btn {
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(119, 221, 213, 0.12);
  color: rgba(245, 255, 252, 0.92);
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s ease, transform 0.2s ease;
}

.sidebar-new-btn:hover {
  background: rgba(119, 221, 213, 0.18);
  transform: translateY(-1px);
}

.sidebar-section {
  flex: 1;
  min-height: 0;
}

.sidebar-section-title {
  padding: 6px 8px 10px;
  color: rgba(119, 221, 213, 0.7);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.sidebar-list {
  display: grid;
  gap: 8px;
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  padding-right: 4px;
}

.sidebar-state {
  padding: 12px 10px;
  color: rgba(226, 241, 239, 0.55);
  font-size: 0.86rem;
  line-height: 1.6;
}

.sidebar-item {
  display: grid;
  gap: 8px;
  padding: 12px 12px 11px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
  color: rgba(245, 255, 252, 0.88);
  transition: background 0.2s ease, transform 0.2s ease;
}

.sidebar-item:hover {
  background: rgba(119, 221, 213, 0.12);
  transform: translateX(2px);
}

.sidebar-item.active {
  background: rgba(119, 221, 213, 0.16);
  box-shadow: inset 0 0 0 1px rgba(119, 221, 213, 0.2);
}

.sidebar-item-name {
  font-size: 0.92rem;
  font-weight: 600;
  line-height: 1.35;
}

.sidebar-item-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: rgba(226, 241, 239, 0.54);
  font-size: 0.76rem;
}

.sidebar-status {
  display: inline-flex;
  align-items: center;
  padding: 3px 7px;
  border-radius: 999px;
  font-weight: 700;
}

.sidebar-status.is-complete {
  background: rgba(84, 198, 162, 0.14);
  color: #8bf2d4;
}

.sidebar-status.is-live {
  background: rgba(119, 221, 213, 0.14);
  color: #7deae2;
}

.sidebar-status.is-failed {
  background: rgba(255, 120, 120, 0.14);
  color: #ff9b9b;
}

.sidebar-status.is-draft {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(245, 255, 252, 0.74);
}

.sidebar-user {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
}

.project-sidebar.embedded .sidebar-user {
  margin-top: 14px;
}

.sidebar-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  object-fit: cover;
}

.sidebar-avatar.fallback {
  display: grid;
  place-items: center;
  background: rgba(119, 221, 213, 0.18);
  color: #e8fffb;
  font-size: 0.88rem;
  font-weight: 700;
}

.sidebar-user-copy {
  min-width: 0;
}

.sidebar-user-name {
  color: rgba(245, 255, 252, 0.9);
  font-size: 0.88rem;
  font-weight: 600;
}

.sidebar-user-email {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(226, 241, 239, 0.52);
  font-size: 0.74rem;
}

@media (max-width: 1100px) {
  .project-sidebar {
    display: none;
  }
}
</style>
