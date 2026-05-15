<template>
  <div class="simulation-panel">
    <!-- Top Control Bar -->
    <div class="control-bar">
      <div class="status-group">
        <!-- Progresso de la plataforma Twitter -->
        <div class="platform-status twitter" :class="{ active: runStatus.twitter_running, completed: runStatus.twitter_completed }">
          <div class="platform-header">
            <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
            </svg>
            <span class="platform-name">{{ $t('step3.platformInfoPlaza') }}</span>
            <span v-if="runStatus.twitter_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">{{ $t('step3.roundShort') }}</span>
              <span class="stat-value mono">{{ runStatus.twitter_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">{{ $t('step3.timeShort') }}</span>
              <span class="stat-value mono">{{ twitterElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">{{ $t('step3.actsShort') }}</span>
              <span class="stat-value mono">{{ runStatus.twitter_actions_count || 0 }}</span>
            </span>
          </div>
          <!-- sugerencia de acciones disponibles -->
          <div class="actions-tooltip">
            <div class="tooltip-title">{{ $t('step3.availableActions') }}</div>
            <div class="tooltip-actions">
              <span class="tooltip-action">POST</span>
              <span class="tooltip-action">LIKE</span>
              <span class="tooltip-action">REPOST</span>
              <span class="tooltip-action">QUOTE</span>
              <span class="tooltip-action">FOLLOW</span>
              <span class="tooltip-action">IDLE</span>
            </div>
          </div>
        </div>
        
        <!-- Progresso de la plataforma Reddit -->
        <div class="platform-status reddit" :class="{ active: runStatus.reddit_running, completed: runStatus.reddit_completed }">
          <div class="platform-header">
            <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            <span class="platform-name">{{ $t('step3.platformTopicCommunity') }}</span>
            <span v-if="runStatus.reddit_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">{{ $t('step3.roundShort') }}</span>
              <span class="stat-value mono">{{ runStatus.reddit_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">{{ $t('step3.timeShort') }}</span>
              <span class="stat-value mono">{{ redditElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">{{ $t('step3.actsShort') }}</span>
              <span class="stat-value mono">{{ runStatus.reddit_actions_count || 0 }}</span>
            </span>
          </div>
          <!-- sugerencia de acciones disponibles -->
          <div class="actions-tooltip">
            <div class="tooltip-title">{{ $t('step3.availableActions') }}</div>
            <div class="tooltip-actions">
              <span class="tooltip-action">POST</span>
              <span class="tooltip-action">COMMENT</span>
              <span class="tooltip-action">LIKE</span>
              <span class="tooltip-action">DISLIKE</span>
              <span class="tooltip-action">SEARCH</span>
              <span class="tooltip-action">TREND</span>
              <span class="tooltip-action">FOLLOW</span>
              <span class="tooltip-action">MUTE</span>
              <span class="tooltip-action">REFRESH</span>
              <span class="tooltip-action">IDLE</span>
            </div>
          </div>
        </div>
      </div>

      <div class="action-controls">
        <button 
          class="action-btn primary"
          :disabled="phase !== 2 || isGeneratingReport"
          @click="handleNextStep"
        >
          <span v-if="isGeneratingReport" class="loading-spinner-small"></span>
          {{ isGeneratingReport ? $t('step3.generatingReportBtn') : $t('step3.startGenerateReportBtn') }}
          <span v-if="!isGeneratingReport" class="arrow-icon">→</span>
        </button>
      </div>
    </div>

    <!-- Main Content: Dual Timeline -->
    <div class="main-content-area" ref="scrollContainer">
      <!-- Timeline Header -->
      <div class="timeline-header" v-if="allActions.length > 0">
        <div class="timeline-stats">
          <span class="total-count">{{ $t('step3.totalEvents') }}: <span class="mono">{{ allActions.length }}</span></span>
          <span class="platform-breakdown">
            <span class="breakdown-item twitter">
              <svg class="mini-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
              <span class="mono">{{ twitterActionsCount }}</span>
            </span>
            <span class="breakdown-divider">/</span>
            <span class="breakdown-item reddit">
              <svg class="mini-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
              <span class="mono">{{ redditActionsCount }}</span>
            </span>
          </span>
        </div>
      </div>
      
      <!-- Timeline Feed -->
      <div class="timeline-feed">
        <div class="timeline-axis"></div>
        
        <TransitionGroup name="timeline-item">
          <div 
            v-for="action in chronologicalActions" 
            :key="action._uniqueId || action.id || `${action.timestamp}-${action.agent_id}`" 
            class="timeline-item"
            :class="action.platform"
          >
            <div class="timeline-marker">
              <div class="marker-dot"></div>
            </div>
            
            <div class="timeline-card">
              <div class="card-header">
                <div class="agent-info">
                  <div class="avatar-placeholder">{{ (action.agent_name || 'A')[0] }}</div>
                  <span class="agent-name">{{ action.agent_name }}</span>
                </div>
                
                <div class="header-meta">
                  <div class="platform-indicator">
                    <svg v-if="action.platform === 'twitter'" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                    <svg v-else viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                  </div>
                  <div class="action-badge" :class="getActionTypeClass(action.action_type)">
                    {{ getActionTypeLabel(action.action_type) }}
                  </div>
                </div>
              </div>
              
              <div class="card-body">
                <!-- CREATE_POST: Publicar post -->
                <div v-if="action.action_type === 'CREATE_POST' && action.action_args?.content" class="content-text main-text">
                  {{ action.action_args.content }}
                </div>

                <!-- QUOTE_POST: Citar post -->
                <template v-if="action.action_type === 'QUOTE_POST'">
                  <div v-if="action.action_args?.quote_content" class="content-text">
                    {{ action.action_args.quote_content }}
                  </div>
                  <div v-if="action.action_args?.original_content" class="quoted-block">
                    <div class="quote-header">
                      <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                      <span class="quote-label">@{{ action.action_args.original_author_name || 'User' }}</span>
                    </div>
                    <div class="quote-text">
                      {{ truncateContent(action.action_args.original_content, 150) }}
                    </div>
                  </div>
                </template>

                <!-- REPOST: Republicar post -->
                <template v-if="action.action_type === 'REPOST'">
                  <div class="repost-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
                    <span class="repost-label">{{ $t('step3.repostedFrom') }} @{{ action.action_args?.original_author_name || $t('common.unknown') }}</span>
                  </div>
                  <div v-if="action.action_args?.original_content" class="repost-content">
                    {{ truncateContent(action.action_args.original_content, 200) }}
                  </div>
                </template>

                <!-- LIKE_POST: Dar me gusta a la publicación -->
                <template v-if="action.action_type === 'LIKE_POST'">
                  <div class="like-info">
                    <svg class="icon-small filled" viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                    <span class="like-label">{{ $t('step3.likedPostOf') }} @{{ action.action_args?.post_author_name || $t('common.unknown') }}</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="liked-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <!-- CREATE_COMMENT: Publicar comentario -->
                <template v-if="action.action_type === 'CREATE_COMMENT'">
                  <div v-if="action.action_args?.content" class="content-text">
                    {{ action.action_args.content }}
                  </div>
                  <div v-if="action.action_args?.post_id" class="comment-context">
                    <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                    <span>{{ $t('step3.replyToPost') }} #{{ action.action_args.post_id }}</span>
                  </div>
                </template>

                <!-- SEARCH_POSTS: Buscar publicaciones -->
                <template v-if="action.action_type === 'SEARCH_POSTS'">
                  <div class="search-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span class="search-label">{{ $t('step3.searchQuery') }}:</span>
                    <span class="search-query">"{{ action.action_args?.query || '' }}"</span>
                  </div>
                </template>

                <!-- FOLLOW: Seguir usuario -->
                <template v-if="action.action_type === 'FOLLOW'">
                  <div class="follow-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                    <span class="follow-label">{{ $t('step3.followedUser') }} @{{ action.action_args?.target_user || action.action_args?.user_id || $t('common.unknown') }}</span>
                  </div>
                </template>

                <!-- UPVOTE / DOWNVOTE -->
                <template v-if="action.action_type === 'UPVOTE_POST' || action.action_type === 'DOWNVOTE_POST'">
                  <div class="vote-info">
                    <svg v-if="action.action_type === 'UPVOTE_POST'" class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>
                    <svg v-else class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    <span class="vote-label">{{ action.action_type === 'UPVOTE_POST' ? $t('step3.upvotedPost') : $t('step3.downvotedPost') }}</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="voted-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <!-- DO_NOTHING: Sin operación (inactivo) -->
                <template v-if="action.action_type === 'DO_NOTHING'">
                  <div class="idle-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span class="idle-label">{{ $t('step3.actionSkipped') }}</span>
                  </div>
                </template>

                <!-- Fallback genérico: tipo desconocido o con contenido sin procesar -->
                <div v-if="!['CREATE_POST', 'QUOTE_POST', 'REPOST', 'LIKE_POST', 'CREATE_COMMENT', 'SEARCH_POSTS', 'FOLLOW', 'UPVOTE_POST', 'DOWNVOTE_POST', 'DO_NOTHING'].includes(action.action_type) && action.action_args?.content" class="content-text">
                  {{ action.action_args.content }}
                </div>
              </div>

              <div class="card-footer">
                <span class="time-tag">R{{ action.round_num }} • {{ formatActionTime(action.timestamp) }}</span>
                <!-- Platform tag removed as it is in header now -->
              </div>
            </div>
          </div>
        </TransitionGroup>

        <div v-if="allActions.length === 0" class="waiting-state">
          <div class="pulse-ring"></div>
          <span>{{ $t('step3.waitingForAgentActions') }}</span>
        </div>
      </div>
    </div>

    <!-- Bottom Info / Logs -->
    <div class="system-logs" :class="{ collapsed: logsCollapsed }">
      <button class="log-header log-toggle" type="button" @click="logsCollapsed = !logsCollapsed">
        <div class="log-header-left">
          <span class="log-title">{{ $t('mainView.systemDashboard') }}</span>
          <span class="log-id">{{ simulationId || 'NO_SIMULATION' }}</span>
        </div>
        <span class="log-toggle-icon" :class="{ open: !logsCollapsed }">⌄</span>
      </button>
      <div v-show="!logsCollapsed" class="log-content" ref="logContent">
        <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ translateLog(log.msg) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  startSimulation,
  stopSimulation,
  getRunStatus,
  getRunStatusDetail
} from '../api/simulation'
import { generateReport } from '../api/report'
import { useTranslateLog } from '../composables/useTranslateLog'

const { t } = useI18n({ useScope: 'global' })
const { translateLog } = useTranslateLog()

const props = defineProps({
  simulationId: String,
  maxRounds: Number, // número máximo de rondas desde Step2
  minutesPerRound: {
    type: Number,
    default: 30 // por defecto 30 minutos por ronda
  },
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])

const router = useRouter()

// State
const isGeneratingReport = ref(false)
  const phase = ref(0) // 0: no iniciado, 1: en ejecución, 2: completado
const isStarting = ref(false)
const isStopping = ref(false)
const startError = ref(null)
const runStatus = ref({})
  const allActions = ref([]) // todas las acciones (acumulado incrementalmente）
  const actionIds = ref(new Set()) // Conjunto de IDs de acciones para deduplicación
const scrollContainer = ref(null)
const logsCollapsed = ref(true)

// Computed
// Mostrar acciones en orden cronológico (más reciente al final, es decir, al fondo)
const chronologicalActions = computed(() => {
  return allActions.value
})

// Conteo de acciones por plataforma
const twitterActionsCount = computed(() => {
  return allActions.value.filter(a => a.platform === 'twitter').length
})

const redditActionsCount = computed(() => {
  return allActions.value.filter(a => a.platform === 'reddit').length
})

// Formatear el tiempo transcurrido de simulación (según rondas y minutos por ronda)
const formatElapsedTime = (currentRound) => {
  if (!currentRound || currentRound <= 0) return '0h 0m'
  const totalMinutes = currentRound * props.minutesPerRound
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h ${minutes}m`
}

// Tiempo de simulación de la plataforma Twitter
const twitterElapsedTime = computed(() => {
  return formatElapsedTime(runStatus.value.twitter_current_round || 0)
})

// Tiempo de simulación de la plataforma Reddit
const redditElapsedTime = computed(() => {
  return formatElapsedTime(runStatus.value.reddit_current_round || 0)
})

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

  // Restablecer todo el estado (para reiniciar la simulación)
const resetAllState = () => {
  phase.value = 0
  runStatus.value = {}
  allActions.value = []
  actionIds.value = new Set()
  prevTwitterRound.value = 0
  prevRedditRound.value = 0
  startError.value = null
  isStarting.value = false
  isStopping.value = false
  stopPolling()  // detener consultas de rondas previas
}

// iniciar simulación
const doStartSimulation = async () => {
  if (!props.simulationId) {
    addLog(t('log.errorMissingSimId'))
    return
  }

  // Restablecer todos los estados primero para evitar la influencia de la simulación anterior
  resetAllState()
  
  isStarting.value = true
  startError.value = null
  addLog(t('log.startingDualSim'))
  emit('update-status', 'processing')
  
  try {
    const params = {
      simulation_id: props.simulationId,
      platform: 'parallel',
      force: true,  // Forzar reinicio
      enable_graph_memory_update: false  // Deshabilitado por defecto para evitar errores con Zep no disponible
    }
    
    if (props.maxRounds) {
      params.max_rounds = props.maxRounds
      addLog(t('log.setMaxRounds', { rounds: props.maxRounds }))
    }
    
    addLog(t('log.graphMemoryUpdateEnabled'))
    
    const res = await startSimulation(params)
    
    if (res.success && res.data) {
      if (res.data.force_restarted) {
        addLog(t('log.oldSimCleared'))
      }
      addLog(t('log.engineStarted'))
      addLog(`  ├─ PID: ${res.data.process_pid || '-'}`)
      
      phase.value = 1
      runStatus.value = res.data
      
      startStatusPolling()
      startDetailPolling()
    } else {
      startError.value = res.error || 'inicio fallido'
      addLog(t('log.startFailed', { error: res.error || t('common.unknownError') }))
      emit('update-status', 'error')
    }
  } catch (err) {
    startError.value = err.message
    addLog(t('log.startException', { error: err.message }))
    emit('update-status', 'error')
  } finally {
    isStarting.value = false
  }
}

// detener simulación
const handleStopSimulation = async () => {
  if (!props.simulationId) return
  
  isStopping.value = true
  addLog(t('log.stoppingSim'))
  
  try {
    const res = await stopSimulation({ simulation_id: props.simulationId })
    
    if (res.success) {
      addLog(t('log.simStoppedSuccess'))
      phase.value = 2
      stopPolling()
      emit('update-status', 'completed')
    } else {
      addLog(t('log.stopFailed', { error: res.error || t('common.unknownError') }))
    }
  } catch (err) {
    addLog(t('log.stopException', { error: err.message }))
  } finally {
    isStopping.value = false
  }
}

// consultar estado
let statusTimer = null
let detailTimer = null

const startStatusPolling = () => {
  fetchRunStatus()
  statusTimer = setInterval(fetchRunStatus, 2000)
}

const startDetailPolling = () => {
  fetchRunStatusDetail()
  detailTimer = setInterval(fetchRunStatusDetail, 3000)
}

const stopPolling = () => {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
  if (detailTimer) {
    clearInterval(detailTimer)
    detailTimer = null
  }
}

// rastrear la ronda anterior de cada plataforma para detectar cambios y generar logs
const prevTwitterRound = ref(0)
const prevRedditRound = ref(0)

const fetchRunStatus = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getRunStatus(props.simulationId)
    
    if (res.success && res.data) {
      const data = res.data
      
      runStatus.value = data

      if (data.runner_status === 'failed') {
        const backendError = data.error || t('common.unknownError')
        addLog(t('log.startFailed', { error: backendError }))
        startError.value = backendError
        stopPolling()
        emit('update-status', 'error')
        return
      }
      
      // Detectar cambios de rondas en cada plataforma y generar logs
      if (data.twitter_current_round > prevTwitterRound.value) {
        addLog(`[Plaza] R${data.twitter_current_round}/${data.total_rounds} | T:${data.twitter_simulated_hours || 0}h | A:${data.twitter_actions_count}`)
        prevTwitterRound.value = data.twitter_current_round
      }
      
      if (data.reddit_current_round > prevRedditRound.value) {
        addLog(`[Comunidad] R${data.reddit_current_round}/${data.total_rounds} | T:${data.reddit_simulated_hours || 0}h | A:${data.reddit_actions_count}`)
        prevRedditRound.value = data.reddit_current_round
      }
      
      // detectar si la simulación completada (mediante runner_status o estado de plataforma)
      const isCompleted = data.runner_status === 'completed' || data.runner_status === 'stopped'
      
      // verificación adicional: si el backend aún no actualizó runner_status pero la plataforma ya completó
      // mediante detectar twitter_completed y reddit_completed
      const platformsCompleted = checkPlatformsCompleted(data)
      
      if (isCompleted || platformsCompleted) {
        if (platformsCompleted && !isCompleted) {
          addLog(t('log.allPlatformsCompleted'))
        }
        addLog(t('log.simCompleted'))
        phase.value = 2
        stopPolling()
        emit('update-status', 'completed')
      }
    }
  } catch (err) {
    console.warn('obtención de estado de ejecución fallida:', err)
  }
}

// verificar si todas las plataformas habilitadas completaron
const checkPlatformsCompleted = (data) => {
  // si no hay datos de plataforma, volver false
  if (!data) return false
  
  // verificar el estado de finalización de cada plataforma
  const twitterCompleted = data.twitter_completed === true
  const redditCompleted = data.reddit_completed === true
  
  // si al menos una plataforma completó, verificar si todas las plataformas habilitadas completaron
  // verificar si la plataforma está habilitada mediante actions_count (si count > 0 o running fue true)
  const twitterEnabled = (data.twitter_actions_count > 0) || data.twitter_running || twitterCompleted
  const redditEnabled = (data.reddit_actions_count > 0) || data.reddit_running || redditCompleted
  
  // si ninguna plataforma está habilitada, volver false
  if (!twitterEnabled && !redditEnabled) return false
  
  // verificar si todas las plataformas habilitadas completaron
  if (twitterEnabled && !twitterCompleted) return false
  if (redditEnabled && !redditCompleted) return false
  
  return true
}

const fetchRunStatusDetail = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getRunStatusDetail(props.simulationId)
    
    if (res.success && res.data) {
      // usar all_actions para obtener la lista completa de acciones
      const serverActions = res.data.all_actions || []
      
      // agregar nuevas acciones de forma incremental (deduplicación)
      let newActionsAdded = 0
      serverActions.forEach(action => {
        // generar ID único
        const actionId = action.id || `${action.timestamp}-${action.platform}-${action.agent_id}-${action.action_type}`
        
        if (!actionIds.value.has(actionId)) {
          actionIds.value.add(actionId)
          allActions.value.push({
            ...action,
            _uniqueId: actionId
          })
          newActionsAdded++
        }
      })
      
      // no desplazamiento automático para que el usuario vea la línea de tiempo libremente
      // nuevas acciones se agregan al final
    }
  } catch (err) {
    console.warn('obtención de estado detallado fallida:', err)
  }
}

// Helpers
const getActionTypeLabel = (type) => {
  const labels = {
    'CREATE_POST': 'POST',
    'REPOST': 'REPOST',
    'LIKE_POST': 'LIKE',
    'CREATE_COMMENT': 'COMMENT',
    'LIKE_COMMENT': 'LIKE',
    'DO_NOTHING': 'IDLE',
    'FOLLOW': 'FOLLOW',
    'SEARCH_POSTS': 'SEARCH',
    'QUOTE_POST': 'QUOTE',
    'UPVOTE_POST': 'UPVOTE',
    'DOWNVOTE_POST': 'DOWNVOTE'
  }
  return labels[type] || type || 'UNKNOWN'
}

const getActionTypeClass = (type) => {
  const classes = {
    'CREATE_POST': 'badge-post',
    'REPOST': 'badge-action',
    'LIKE_POST': 'badge-action',
    'CREATE_COMMENT': 'badge-comment',
    'LIKE_COMMENT': 'badge-action',
    'QUOTE_POST': 'badge-post',
    'FOLLOW': 'badge-meta',
    'SEARCH_POSTS': 'badge-meta',
    'UPVOTE_POST': 'badge-action',
    'DOWNVOTE_POST': 'badge-action',
    'DO_NOTHING': 'badge-idle'
  }
  return classes[type] || 'badge-default'
}

const truncateContent = (content, maxLength = 100) => {
  if (!content) return ''
  if (content.length > maxLength) return content.substring(0, maxLength) + '...'
  return content
}

const formatActionTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const handleNextStep = async () => {
  if (!props.simulationId) {
    addLog(t('log.errorMissingSimId'))
    return
  }

  if (isGeneratingReport.value) {
    addLog(t('log.reportRequestSent'))
    return
  }
  
  isGeneratingReport.value = true
  addLog(t('log.startingReportGen'))
  
  try {
    const res = await generateReport({
      simulation_id: props.simulationId,
      force_regenerate: true
    })
    
    if (res.success && res.data) {
      const reportId = res.data.report_id
      addLog(t('log.reportGenTaskStarted', { reportId }))
      
      // saltar a la página del informe
      router.push({ name: 'Report', params: { reportId } })
    } else {
      addLog(t('log.reportGenFailed', { error: res.error || t('common.unknownError') }))
      isGeneratingReport.value = false
    }
  } catch (err) {
    addLog(t('log.reportGenException', { error: err.message }))
    isGeneratingReport.value = false
  }
}

// Scroll log to bottom
const logContent = ref(null)
watch(() => props.systemLogs?.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})

onMounted(() => {
  addLog(t('log.step3Init'))
  if (props.simulationId) {
    doStartSimulation()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.simulation-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  overflow: hidden;
}

/* --- Control Bar --- */
.control-bar {
  background: #FFF;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #EAEAEA;
  z-index: 10;
  height: 64px;
}

.status-group {
  display: flex;
  gap: 12px;
}

/* Platform Status Cards */
.platform-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 4px;
  background: #FAFAFA;
  border: 1px solid #EAEAEA;
  opacity: 0.7;
  transition: all 0.3s;
  min-width: 140px;
  position: relative;
  cursor: pointer;
}

.platform-status.active {
  opacity: 1;
  border-color: #333;
  background: #FFF;
}

.platform-status.completed {
  opacity: 1;
  border-color: #1A936F;
  background: #F2FAF6;
}

/* Actions Tooltip */
.actions-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  padding: 10px 14px;
  background: #000;
  color: #FFF;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 100;
  min-width: 180px;
  pointer-events: none;
}

.actions-tooltip::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid #000;
}

.platform-status:hover .actions-tooltip {
  opacity: 1;
  visibility: visible;
}

.tooltip-title {
  font-size: 10px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.tooltip-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tooltip-action {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  color: #FFF;
  letter-spacing: 0.03em;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.platform-name {
  font-size: 11px;
  font-weight: 700;
  color: #000;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.platform-status.twitter .platform-icon { color: #000; }
.platform-status.reddit .platform-icon { color: #000; }

.platform-stats {
  display: flex;
  gap: 10px;
}

.stat {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.stat-label {
  font-size: 8px;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 11px;
  font-weight: 600;
  color: #333;
}

.stat-total, .stat-unit {
  font-size: 9px;
  color: #999;
  font-weight: 400;
}

.status-badge {
  margin-left: auto;
  color: #1A936F;
  display: flex;
  align-items: center;
}

/* Action Button */
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.action-btn.primary {
  background: #000;
  color: #FFF;
}

.action-btn.primary:hover:not(:disabled) {
  background: #333;
}

.action-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* --- Main Content Area --- */
.main-content-area {
  flex: 1;
  overflow-y: auto;
  position: relative;
  background: #FFF;
}

/* Timeline Header */
.timeline-header {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  padding: 12px 24px;
  border-bottom: 1px solid #EAEAEA;
  z-index: 5;
  display: flex;
  justify-content: center;
}

.timeline-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 11px;
  color: #666;
  background: #F5F5F5;
  padding: 4px 12px;
  border-radius: 20px;
}

.total-count {
  font-weight: 600;
  color: #333;
}

.platform-breakdown {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.breakdown-divider { color: #DDD; }
.breakdown-item.twitter { color: #000; }
.breakdown-item.reddit { color: #000; }

/* --- Timeline Feed --- */
.timeline-feed {
  padding: 24px 0;
  position: relative;
  min-height: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.timeline-axis {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: #EAEAEA; /* Cleaner line */
  transform: translateX(-50%);
}

.timeline-item {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  position: relative;
  width: 100%;
}

.timeline-marker {
  position: absolute;
  left: 50%;
  top: 24px;
  width: 10px;
  height: 10px;
  background: #FFF;
  border: 1px solid #CCC;
  border-radius: 50%;
  transform: translateX(-50%);
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.marker-dot {
  width: 4px;
  height: 4px;
  background: #CCC;
  border-radius: 50%;
}

.timeline-item.twitter .marker-dot { background: #000; }
.timeline-item.reddit .marker-dot { background: #000; }
.timeline-item.twitter .timeline-marker { border-color: #000; }
.timeline-item.reddit .timeline-marker { border-color: #000; }

/* Card Layout */
.timeline-card {
  width: calc(100% - 48px);
  background: #FFF;
  border-radius: 2px;
  padding: 16px 20px;
  border: 1px solid #EAEAEA;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
  position: relative;
  transition: all 0.2s;
}

.timeline-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-color: #DDD;
}

/* Left side (Twitter) */
.timeline-item.twitter {
  justify-content: flex-start;
  padding-right: 50%;
}
.timeline-item.twitter .timeline-card {
  margin-left: auto;
  margin-right: 32px; /* Gap from axis */
}

/* Right side (Reddit) */
.timeline-item.reddit {
  justify-content: flex-end;
  padding-left: 50%;
}
.timeline-item.reddit .timeline-card {
  margin-right: auto;
  margin-left: 32px; /* Gap from axis */
}

/* Card Content Styles */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #F5F5F5;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-placeholder {
  width: 24px;
  height: 24px;
  background: #000;
  color: #FFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.agent-name {
  font-size: 13px;
  font-weight: 600;
  color: #000;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-indicator {
  color: #999;
  display: flex;
  align-items: center;
}

.action-badge {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid transparent;
}

/* Monochromatic Badges */
.badge-post { background: #F0F0F0; color: #333; border-color: #E0E0E0; }
.badge-comment { background: #F0F0F0; color: #666; border-color: #E0E0E0; }
.badge-action { background: #FFF; color: #666; border: 1px solid #E0E0E0; }
.badge-meta { background: #FAFAFA; color: #999; border: 1px dashed #DDD; }
.badge-idle { opacity: 0.5; }

.content-text {
  font-size: 13px;
  line-height: 1.6;
  color: #333;
  margin-bottom: 10px;
}

.content-text.main-text {
  font-size: 14px;
  color: #000;
}

/* Info Blocks (Quote, Repost, etc) */
.quoted-block, .repost-content {
  background: #F9F9F9;
  border: 1px solid #EEE;
  padding: 10px 12px;
  border-radius: 2px;
  margin-top: 8px;
  font-size: 12px;
  color: #555;
}

.quote-header, .repost-info, .like-info, .search-info, .follow-info, .vote-info, .idle-info, .comment-context {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 11px;
  color: #666;
}

.icon-small {
  color: #999;
}
.icon-small.filled {
  color: #999; /* Keep icons neutral unless highlighted */
}

.search-query {
  font-family: 'JetBrains Mono', monospace;
  background: #F0F0F0;
  padding: 0 4px;
  border-radius: 2px;
}

.card-footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  font-size: 10px;
  color: #BBB;
  font-family: 'JetBrains Mono', monospace;
}

/* Waiting State */
.waiting-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #CCC;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.pulse-ring {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #EAEAEA;
  animation: ripple 2s infinite;
}

@keyframes ripple {
  0% { transform: scale(0.8); opacity: 1; border-color: #CCC; }
  100% { transform: scale(2.5); opacity: 0; border-color: #EAEAEA; }
}

/* Animation */
.timeline-item-enter-active,
.timeline-item-leave-active {
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.timeline-item-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.timeline-item-leave-to {
  opacity: 0;
}

/* Logs */
.system-logs {
  background: #000;
  color: #DDD;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid #222;
  flex-shrink: 0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #333;
  padding-bottom: 8px;
  margin-bottom: 8px;
  font-size: 10px;
  color: #666;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  height: 100px;
  overflow-y: auto;
  padding-right: 4px;
}

.log-content::-webkit-scrollbar { width: 4px; }
.log-content::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }

.log-line {
  font-size: 11px;
  display: flex;
  gap: 12px;
  line-height: 1.5;
}

.log-time { color: #555; min-width: 75px; }
.log-msg { color: #BBB; word-break: break-all; }
.mono { font-family: 'JetBrains Mono', monospace; }

/* Loading spinner for button */
.loading-spinner-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 6px;
}

/* --- YouWorld Dark Overrides --- */
.simulation-panel {
  background: transparent;
  color: #edf6f2;
  gap: 14px;
  padding: 0;
}

.control-bar {
  height: auto;
  margin: 0 18px;
  padding: 16px 18px;
  border-radius: 28px;
  border: 1px solid rgba(125, 205, 198, 0.12);
  background: linear-gradient(135deg, rgba(20, 28, 36, 0.96), rgba(27, 18, 38, 0.94));
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.18);
  align-items: stretch;
  gap: 18px;
}

.status-group {
  flex: 1;
  gap: 14px;
  min-width: 0;
}

.platform-status {
  min-width: 0;
  flex: 1 1 0;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  opacity: 1;
  overflow: hidden;
}

.platform-status.active {
  border-color: rgba(110, 208, 200, 0.2);
  background: linear-gradient(135deg, rgba(23, 33, 40, 0.98), rgba(21, 27, 37, 0.98));
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.16);
}

.platform-status.completed {
  border-color: rgba(110, 208, 200, 0.22);
  background: linear-gradient(135deg, rgba(24, 33, 36, 0.96), rgba(19, 22, 32, 0.96));
}

.platform-status.twitter .platform-icon,
.platform-status.reddit .platform-icon,
.platform-indicator,
.icon-small,
.icon-small.filled {
  color: #87d6d1;
}

.platform-name,
.total-count,
.agent-name,
.content-text.main-text {
  color: #edf6f2;
}

.stat-label,
.timeline-stats,
.quote-header,
.repost-info,
.like-info,
.search-info,
.follow-info,
.vote-info,
.idle-info,
.comment-context,
.card-footer,
.log-title,
.log-id {
  color: #8ea5a1;
}

.stat-value,
.content-text,
.quote-text,
.repost-content,
.liked-content,
.voted-content,
.search-query,
.log-msg {
  color: #d8e8e4;
}

.stat-total,
.stat-unit,
.breakdown-divider,
.log-time {
  color: rgba(208, 230, 226, 0.45);
}

.action-btn {
  border-radius: 999px;
  padding: 14px 24px;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
}

.action-btn.primary {
  background: rgba(255, 255, 255, 0.06);
  color: #edf6f2;
  border: 1px solid rgba(110, 208, 200, 0.18);
  box-shadow: none;
}

.action-btn.primary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.09);
}

.action-btn:disabled {
  opacity: 0.45;
}

.main-content-area {
  margin: 0 18px;
  border-radius: 30px;
  border: 0;
  background: transparent;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  padding-right: 8px;
  scrollbar-gutter: stable;
}

.timeline-header {
  top: 0;
  background: transparent;
  border-bottom: 0;
  padding-bottom: 6px;
}

.timeline-stats {
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 999px;
}

.timeline-feed {
  max-width: 980px;
  padding: 12px 18px 40px;
}

.timeline-axis {
  background: linear-gradient(to bottom, rgba(113, 149, 255, 0.12), rgba(110, 208, 200, 0.18), rgba(255, 255, 255, 0.08));
}

.timeline-marker {
  width: 14px;
  height: 14px;
  background: #10161d;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.marker-dot,
.timeline-item.twitter .marker-dot,
.timeline-item.reddit .marker-dot {
  width: 6px;
  height: 6px;
  background: #67d7cd;
}

.timeline-item.twitter .timeline-marker,
.timeline-item.reddit .timeline-marker {
  border-color: rgba(103, 215, 205, 0.35);
}

.timeline-card {
  background: linear-gradient(145deg, rgba(21, 28, 36, 0.96), rgba(28, 18, 40, 0.94));
  border-radius: 26px;
  padding: 18px 20px;
  border: 1px solid rgba(125, 205, 198, 0.08);
  box-shadow: none;
}

.timeline-card:hover {
  border-color: rgba(125, 205, 198, 0.12);
  box-shadow: none;
}

.card-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.avatar-placeholder {
  background: rgba(111, 150, 255, 0.18);
  color: #d8e8e4;
}

.action-badge {
  border-radius: 999px;
  padding: 4px 8px;
}

.badge-post,
.badge-comment,
.badge-action,
.badge-meta,
.badge-idle {
  background: rgba(255, 255, 255, 0.04);
  color: #cfe0dc;
  border-color: rgba(255, 255, 255, 0.06);
}

.quoted-block,
.repost-content,
.search-query {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 18px;
}

.waiting-state {
  color: rgba(221, 238, 235, 0.72);
}

.pulse-ring {
  border-color: rgba(111, 150, 255, 0.2);
}

.system-logs {
  margin: 0 18px 14px;
  padding: 0;
  border: 0;
  background: transparent;
  overflow: visible;
}

.log-header {
  margin: 0;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 0 8px;
  border: 0;
  border-bottom: 1px solid rgba(235, 255, 251, 0.08);
  background: transparent;
  cursor: pointer;
  gap: 12px;
  min-height: auto;
  color: rgba(235, 255, 251, 0.46);
}

.log-toggle {
  appearance: none;
}

.log-header-left {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.log-toggle-icon {
  color: rgba(119, 221, 213, 0.72);
  font-size: 1rem;
  line-height: 1;
  transition: transform 0.2s ease;
}

.log-toggle-icon.open {
  transform: rotate(180deg);
}

.log-content {
  height: 170px;
  padding: 8px 0 0;
}

.system-logs.collapsed .log-content {
  display: none;
}

.system-logs:not(.collapsed) .log-header {
  padding: 0 0 10px;
}

.system-logs:not(.collapsed) .log-content {
  border: 0;
  border-radius: 0;
  background: transparent;
}

.system-logs.collapsed .log-header {
  padding: 0 0 8px;
}

.system-logs.collapsed .log-title,
.system-logs.collapsed .log-id {
  color: #8ea5a1;
}

.log-title,
.log-id {
  color: rgba(235, 255, 251, 0.46);
}

.log-time {
  color: rgba(119, 221, 213, 0.52);
}

.log-msg {
  color: rgba(235, 255, 251, 0.74);
}

.quoted-block,
.repost-content,
.search-query {
  background: rgba(255, 255, 255, 0.04);
  border: 0 !important;
  border-radius: 18px;
}

.timeline-feed > .timeline-item,
.timeline-feed > .waiting-state {
  margin-inline: auto;
}

.main-content-area::-webkit-scrollbar {
  width: 8px;
}

.main-content-area::-webkit-scrollbar-track {
  background: transparent;
}

.main-content-area::-webkit-scrollbar-thumb {
  background: rgba(235, 255, 251, 0.18);
  border-radius: 999px;
}

.main-content-area::-webkit-scrollbar-thumb:hover {
  background: rgba(235, 255, 251, 0.28);
}

@media (max-width: 1200px) {
  .control-bar {
    flex-direction: column;
  }

  .status-group {
    width: 100%;
  }

  .action-controls {
    width: 100%;
  }

  .action-btn.primary {
    width: 100%;
    justify-content: center;
  }
}
</style>

<style>
/* Remove square borders from legacy blocks */
.quoted-block,
.repost-content,
.search-query,
.system-logs {
  outline: none !important;
  box-shadow: none !important;
}

.quoted-block,
.repost-content,
.search-query {
  border: 0 !important;
  background: rgba(255, 255, 255, 0.04) !important;
}

.system-logs {
  border-top: 0 !important;
  border-color: transparent !important;
}

/* Match phase one palette and system panel */
.control-bar,
.timeline-card,
.platform-status,
.timeline-stats {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.035)) !important;
  border: 0 !important;
  box-shadow: none !important;
}

.control-bar {
  box-shadow: none !important;
}

.platform-status.active,
.platform-status.completed {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.035)) !important;
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.12) !important;
}

.platform-name,
.total-count,
.agent-name,
.content-text.main-text,
.timeline-card .content-text,
.timeline-card .quote-text,
.timeline-card .liked-content,
.timeline-card .voted-content {
  color: rgba(244, 255, 251, 0.92) !important;
}

.stat-label,
.timeline-stats,
.quote-header,
.repost-info,
.like-info,
.search-info,
.follow-info,
.vote-info,
.idle-info,
.comment-context,
.card-footer,
.log-title,
.log-id,
.stat-total,
.stat-unit,
.breakdown-divider,
.log-time {
  color: rgba(235, 255, 251, 0.46) !important;
}

.stat-value,
.content-text,
.quote-text,
.repost-content,
.liked-content,
.search-query,
.log-msg {
  color: rgba(235, 255, 251, 0.64) !important;
}

.action-btn.primary {
  background: linear-gradient(90deg, #78ddd5, #a7eee8) !important;
  color: #06100f !important;
  border: 0 !important;
}

.action-btn.primary:hover:not(:disabled) {
  background: linear-gradient(90deg, #78ddd5, #a7eee8) !important;
  filter: brightness(1.03);
}

.badge-post,
.badge-comment,
.badge-action,
.badge-meta,
.badge-idle {
  background: rgba(255, 255, 255, 0.065) !important;
  color: rgba(235, 255, 251, 0.72) !important;
  border-color: transparent !important;
}

.system-logs {
  background: rgba(0, 0, 0, 0.35) !important;
  border-top: 1px solid rgba(235, 255, 251, 0.08) !important;
}

.system-logs.collapsed {
  background: rgba(0, 0, 0, 0.18) !important;
}
</style>
