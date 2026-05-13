<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left header-spacer"></div>
      
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
          <span class="step-num">Paso 2/5</span>
          <span class="step-name">{{ $tm('main.stepNames')[1] }}</span>
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
          :currentPhase="2"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Right Panel: Step2 ConfiguraciÃ³n del entorno -->
      <div class="panel-wrapper right" :style="rightPanelStyle">
        <Step2EnvSetup
          :simulationId="currentSimulationId"
          :projectData="projectData"
          :graphData="graphData"
          :systemLogs="systemLogs"
          @go-back="handleGoBack"
          @next-step="handleNextStep"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step2EnvSetup from '../components/Step2EnvSetup.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation, stopSimulation, getEnvStatus, closeSimulationEnv } from '../api/simulation'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })
const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  simulationId: String
})

// Layout State
const viewMode = ref('split')

// Data State
const currentSimulationId = ref(route.params.simulationId)
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const systemLogs = ref([])
const currentStatus = ref('processing') // processing | completed | error

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
  if (currentStatus.value === 'error') return 'Error'
  if (currentStatus.value === 'completed') return 'Ready'
  return 'Preparing'
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 100) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

// --- Layout Methods ---
const toggleMaximize = (target) => {
  if (viewMode.value === target) {
    viewMode.value = 'split'
  } else {
    viewMode.value = target
  }
}

const handleGoBack = () => {
  // Volver a la pÃ¡gina process
  if (projectData.value?.project_id) {
    router.push({ name: 'Process', params: { projectId: projectData.value.project_id } })
  } else {
    router.push('/')
  }
}

const handleNextStep = (params = {}) => {
  addLog(t('log.enterStep3'))

  // Registrar configuraciÃ³n de rondas de simulaciÃ³n
  if (params.maxRounds) {
    addLog(t('log.customRoundsConfig', { rounds: params.maxRounds }))
  } else {
    addLog(t('log.useAutoRounds'))
  }
  
  // Construir parÃ¡metros de ruta
  const routeParams = {
    name: 'SimulationRun',
    params: { simulationId: currentSimulationId.value }
  }
  
  // Si hay rondas personalizadas, pasar a travÃ©s de parÃ¡metros query
  if (params.maxRounds) {
    routeParams.query = { maxRounds: params.maxRounds }
  }
  
  // Navegar a la pÃ¡gina Step 3
  router.push(routeParams)
}

// --- Data Logic ---

/**
 * Comprobar y cerrar simulaciones en ejecuciÃ³n
 * Cuando el usuario vuelve de Step 3 a Step 2, se asume que quiere salir de la simulaciÃ³n
 */
const checkAndStopRunningSimulation = async () => {
  if (!currentSimulationId.value) return
  
  try {
    // Primero comprobar si el entorno de simulaciÃ³n estÃ¡ vivo
    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog(t('log.detectedSimEnvRunning'))
      
      // Intentar cerrar con gracia el entorno de simulaciÃ³n
      try {
        const closeRes = await closeSimulationEnv({
          simulation_id: currentSimulationId.value,
          timeout: 10  // 10 segundos de tiempo de espera
        })
        
        if (closeRes.success) {
          addLog(t('log.simEnvClosed'))
        } else {
          addLog(t('log.closeSimEnvFailedWithError', { error: closeRes.error || t('common.unknownError') }))
          // Si el cierre elegante falla, intentar detener forzosamente
          await forceStopSimulation()
        }
      } catch (closeErr) {
        addLog(t('log.closeSimEnvException', { error: closeErr.message }))
        // Si el cierre elegante falla debido a una excepciÃ³n, intentar detener forzosamente
        await forceStopSimulation()
      }
    } else {
      // El entorno no se estÃ¡ ejecutando, pero el proceso puede seguir activo, comprobar estado de simulaciÃ³n
      const simRes = await getSimulation(currentSimulationId.value)
      if (simRes.success && simRes.data?.status === 'running') {
        addLog(t('log.detectedSimRunning'))
        await forceStopSimulation()
      }
    }
  } catch (err) {
    // El fallo al verificar el estado del entorno no afecta el flujo subsequente
    console.warn('Fallo al verificar estado de simulaciÃ³n:', err)
  }
}

/**
 * Forzar detenciÃ³n de simulaciÃ³n
 */
const forceStopSimulation = async () => {
  try {
    const stopRes = await stopSimulation({ simulation_id: currentSimulationId.value })
    if (stopRes.success) {
      addLog(t('log.simForceStopSuccess'))
    } else {
      addLog(t('log.forceStopSimFailed', { error: stopRes.error || t('common.unknownError') }))
    }
  } catch (err) {
    addLog(t('log.forceStopSimException', { error: err.message }))
  }
}

const loadSimulationData = async () => {
  try {
    addLog(t('log.loadingSimData', { id: currentSimulationId.value }))

    // Obtener informaciÃ³n de simulaciÃ³n
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data

      // Obtener informaciÃ³n de proyecto
      if (simData.project_id) {
        const projRes = await getProject(simData.project_id)
        if (projRes.success && projRes.data) {
          projectData.value = projRes.data
          addLog(t('log.projectLoadSuccess', { id: projRes.data.project_id }))

          // Obtener datos de grÃ¡fico
          if (projRes.data.graph_id) {
            await loadGraph(projRes.data.graph_id)
          }
        }
      }
    } else {
      addLog(t('log.loadSimDataFailed', { error: simRes.error || t('common.unknownError') }))
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

onMounted(async () => {
  addLog(t('log.simViewInit'))

  // Comprobar y cerrar simulaciones en ejecuciÃ³n (cuando el usuario vuelve de Step 3)
  await checkAndStopRunningSimulation()

  // Cargar datos de simulaciÃ³n
  loadSimulationData()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Inter', 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  background:
    radial-gradient(circle at 72% 8%, rgba(91, 203, 190, 0.2), transparent 30%),
    radial-gradient(circle at 18% 10%, rgba(77, 35, 111, 0.32), transparent 34%),
    linear-gradient(125deg, #050607 0%, #081310 34%, #0b0715 72%, #05020a 100%);
}

/* Header */
.app-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  background: rgba(5, 4, 12, 0.72);
  border-bottom: 1px solid rgba(235, 255, 251, 0.08);
  z-index: 100;
  position: relative;
  backdrop-filter: blur(18px);
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.view-switcher {
  display: flex;
  background: rgba(255, 255, 255, 0.06);
  padding: 5px;
  border-radius: 999px;
  gap: 4px;
  border: 1px solid rgba(235, 255, 251, 0.1);
}

.switch-btn {
  border: none;
  background: transparent;
  padding: 8px 18px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #8fa5a1;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-btn.active {
  background: rgba(119, 221, 213, 0.18);
  color: #edf6f2;
  box-shadow: none;
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
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.3s ease, transform 0.3s ease;
  will-change: width, opacity, transform;
  padding: 14px;
}

.panel-wrapper.left {
  border-right: 0;
  padding-right: 7px;
}

.panel-wrapper.right {
  padding-left: 7px;
}

.header-spacer {
  width: 140px;
  min-width: 140px;
}
</style>


