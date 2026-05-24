<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/')">YOUWORLD</div>
      </div>
      
      <div class="header-center">
        <div class="view-switcher">
          <button 
            v-for="mode in ['graph', 'split', 'workbench']" 
            :key="mode"
            class="switch-btn"
            :class="{ active: viewMode === mode }"
            @click="viewMode = mode"
          >
            {{ { graph: $t('main.layoutGraph'), split: $t('main.layoutSplit'), workbench: $t('main.layoutWorkbench') }[mode] }}
          </button>
        </div>
      </div>

      <div class="header-right">
        <LanguageSwitcher />
        <div class="step-divider"></div>
        <div class="workflow-step">
          <span class="step-num">{{ $t('main.stepCounter', { current: 5 }) }}</span>
          <span class="step-name">{{ $tm('main.stepNames')[4] }}</span>
        </div>
        <div class="step-divider"></div>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="content-area">
      <!-- Left Panel: Graph -->
      <div class="panel-wrapper left" :style="leftPanelStyle">
        <GraphPanel 
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="5"
          :isSimulating="false"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Right Panel: Step5 InteracciÃ³n profunda -->
      <div class="panel-wrapper right" :style="rightPanelStyle">
        <Step5Interaction
          :reportId="currentReportId"
          :simulationId="simulationId"
          :systemLogs="systemLogs"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import GraphPanel from '../components/GraphPanel.vue'
import Step5Interaction from '../components/Step5Interaction.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation } from '../api/simulation'
import { getReport } from '../api/report'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n({ useScope: 'global' })

// Props
const props = defineProps({
  reportId: String
})

// Layout State - por defecto cambiar a vista de Ãrea de trabajo
const viewMode = ref('workbench')

// Data State
const currentReportId = ref(route.params.reportId)
const simulationId = ref(null)
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const projectNotFound = ref(false)
const systemLogs = ref([])
const currentStatus = ref('ready') // ready | processing | completed | error

// --- Computed Layout Styles ---
const leftPanelStyle = computed(() => {
  if (viewMode.value === 'graph') return { width: '100%', opacity: 1, transform: 'translateX(0)' }
  if (viewMode.value === 'workbench') return { width: '0%', opacity: 0, transform: 'translateX(-20px)' }
  return { width: '50%', opacity: 1, transform: 'translateX(0)' }
})

const rightPanelStyle = computed(() => {
  if (viewMode.value === 'workbench') return { width: '100%', opacity: 1, transform: 'translateX(0)' }
  if (viewMode.value === 'graph') return { width: '0%', opacity: 0, transform: 'translateX(20px)' }
  return { width: '50%', opacity: 1, transform: 'translateX(0)' }
})

// --- Status Computed ---
const statusClass = computed(() => {
  return currentStatus.value
})

const statusText = computed(() => {
  if (currentStatus.value === 'error') return t('common.error')
  if (currentStatus.value === 'completed') return t('common.completed')
  if (currentStatus.value === 'processing') return t('common.processing')
  return t('common.ready')
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 200) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

const rememberProjectRoute = (projectId) => {
  if (!projectId || !currentReportId.value) return
  localStorage.setItem(`youworld:project-report:${projectId}`, currentReportId.value)
  localStorage.setItem(
    `youworld:last-project-route:${projectId}`,
    `/interaction/${currentReportId.value}`
  )
}

// --- Layout Methods ---
const toggleMaximize = (target) => {
  if (viewMode.value === target) {
    viewMode.value = 'split'
  } else {
    viewMode.value = target
  }
}

// --- Data Logic ---
const loadReportData = async () => {
  try {
    addLog(t('log.loadReportData', { id: currentReportId.value }))

    // obtener info del report para obtener simulation_id
    const reportRes = await getReport(currentReportId.value)
    if (reportRes.success && reportRes.data) {
      const reportData = reportRes.data
      simulationId.value = reportData.simulation_id

      if (simulationId.value) {
        // obtener info de simulation
        const simRes = await getSimulation(simulationId.value)
        if (simRes.success && simRes.data) {
          const simData = simRes.data

          // obtener info del proyecto (no bloqueante â€” el panel de grafo es enriquecimiento)
          if (simData.project_id) {
            try {
              const projRes = await getProject(simData.project_id)
              if (projRes.success && projRes.data) {
                projectData.value = projRes.data
                rememberProjectRoute(projRes.data.project_id)
                addLog(t('log.projectLoadSuccess', { id: projRes.data.project_id }))

                // obtener datos del grafo
                if (projRes.data.graph_id) {
                  await loadGraph(projRes.data.graph_id)
                }
              }
            } catch (projErr) {
              // 404 u otro error â€” proyecto no disponible, continuar sin Ã©l
              projectNotFound.value = true
              addLog(t('api.projectNotFound', { id: simData.project_id }))
              projectData.value = null
              graphData.value = null
            }
          }
        }
      }
    } else {
      addLog(t('log.getReportInfoFailed', { error: reportRes.error || t('common.unknownError') }))
    }
  } catch (err) {
    addLog(t('log.loadException', { error: err.message }))
  }
}

const loadGraph = async (graphId) => {
  graphLoading.value = true
  
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog(t('log.graphDataLoadSuccess'))
    }
  } catch (err) {
    addLog(t('log.graphLoadFailed', { error: err.message }))
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

// Watch route params
watch(() => route.params.reportId, (newId) => {
  if (newId && newId !== currentReportId.value) {
    currentReportId.value = newId
    loadReportData()
  }
}, { immediate: true })

onMounted(() => {
  addLog(t('log.interactionViewInit'))
  loadReportData()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 72% 8%, rgba(91, 203, 190, 0.2), transparent 30%),
    radial-gradient(circle at 18% 10%, rgba(77, 35, 111, 0.32), transparent 34%),
    linear-gradient(125deg, #050607 0%, #081310 34%, #0b0715 72%, #05020a 100%);
  overflow: hidden;
  font-family: 'Inter', 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

/* Header */
.app-header {
  height: 72px;
  border-bottom: 1px solid rgba(235, 255, 251, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  background: rgba(5, 4, 12, 0.72);
  backdrop-filter: blur(18px);
  z-index: 100;
  position: relative;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 1px;
  cursor: pointer;
  color: #edf6f2;
}

.view-switcher {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(235, 255, 251, 0.08);
  padding: 5px;
  border-radius: 999px;
  gap: 4px;
}

.switch-btn {
  border: none;
  background: transparent;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #8fa5a1;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-btn.active {
  background: rgba(119, 221, 213, 0.16);
  color: #eafffb;
  box-shadow: inset 0 0 0 1px rgba(119, 221, 213, 0.22);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #6ed0c8;
}

.step-name {
  font-weight: 700;
  color: #edf6f2;
}

.step-divider {
  width: 1px;
  height: 14px;
  background-color: rgba(255,255,255,0.12);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #8fa5a1;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #CCC;
}

.status-indicator.ready .dot { background: #6ed0c8; }
.status-indicator.processing .dot { background: #f6a04d; animation: pulse 1s infinite; }
.status-indicator.completed .dot { background: #6ed0c8; }
.status-indicator.error .dot { background: #ff7a7a; }

@keyframes pulse { 50% { opacity: 0.5; } }

/* Content */
.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
  background: transparent;
}

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  padding: 0 14px 14px;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.3s ease, transform 0.3s ease;
  will-change: width, opacity, transform;
}

.panel-wrapper.left {
  border-right: 0;
  padding-right: 7px;
}

.panel-wrapper.right {
  padding-left: 7px;
}
</style>

