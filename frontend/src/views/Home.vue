<template>
  <div class="home-container">
    <Transition name="screen-flow" mode="out-in">
    <section v-if="showIntro" key="intro" class="intro-screen">
      <div class="intro-grid"></div>
      <button class="intro-auth-link" @click="openAuthGate">
        {{ authCtaLabel }}
      </button>
      <div class="intro-shell">
        <p class="intro-eyebrow">{{ $t('home.introEyebrow') }}</p>
        <h1 class="intro-title">YouWorld</h1>
        <p class="intro-copy">{{ $t('home.introDescription') }}</p>

        <div v-if="!hasChosenLanguage" class="intro-actions">
          <span class="intro-action-label">{{ $t('home.chooseLanguage') }}</span>
          <div class="intro-language-list">
            <button
              v-for="localeOption in introLocales"
              :key="localeOption.key"
              class="intro-language-btn"
              @click="chooseLanguage(localeOption.key)"
            >
              {{ localeOption.label }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <div v-else key="app" class="app-shell">
    <!-- Barra de navegación superior -->
    <nav class="navbar">
      <div class="nav-left">
        <button class="nav-brand" @click="activeInfoPanel = null">YOUWORLD</button>
        <div class="nav-info-tabs">
          <button
            v-for="tab in infoTabs"
            :key="tab.key"
            class="nav-info-tab"
            :class="{ active: activeInfoPanel === tab.key }"
            @click="toggleInfoPanel(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
      <div class="nav-links">
        <button class="nav-auth-btn" @click="openAuthGate">
          {{ authCtaLabel }}
        </button>
      </div>
    </nav>

    <div class="main-content">
      <section v-if="activeInfoPanel" class="section-page">
        <button class="section-back" @click="activeInfoPanel = null">← {{ $t('common.back') }}</button>
        <p class="section-kicker">YouWorld</p>
        <h1>{{ activeInfoContent.title }}</h1>
        <div v-if="activeInfoPanel === 'how'" class="section-split">
          <div class="section-copy">
            <p v-for="paragraph in howParagraphs" :key="paragraph">{{ paragraph }}</p>
          </div>
          <div class="world-preview-placeholder">
            <span>{{ $t('home.worldPreviewPlaceholder') }}</span>
          </div>
        </div>
        <div v-else-if="activeInfoPanel === 'why'" class="section-copy wide">
          <p v-for="paragraph in whyParagraphs" :key="paragraph">{{ paragraph }}</p>
        </div>
        <ol v-else class="section-steps">
          <li v-for="step in workflowDetails" :key="step.title">
            <span>{{ step.title }}</span>
            <p>{{ step.desc }}</p>
          </li>
        </ol>
      </section>

      <!-- Sección superior: área Hero -->
      <section v-if="false" class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">{{ $t('home.tagline') }}</span>
            <span class="version-text">{{ $t('home.version') }}</span>
          </div>
          
          <h1 class="main-title">
            {{ $t('home.heroTitle1') }}<br>
            <span class="gradient-text">{{ $t('home.heroTitle2') }}</span>
          </h1>
          
          <div class="hero-desc">
            <p>
              <i18n-t keypath="home.heroDesc" tag="span">
                <template #brand><span class="highlight-bold">{{ $t('home.heroDescBrand') }}</span></template>
                <template #agentScale><span class="highlight-orange">{{ $t('home.heroDescAgentScale') }}</span></template>
                <template #optimalSolution><span class="highlight-code">{{ $t('home.heroDescOptimalSolution') }}</span></template>
              </i18n-t>
            </p>
            <p class="slogan-text">
              {{ $t('home.slogan') }}<span class="blinking-cursor">_</span>
            </p>
          </div>
           
          <div class="decoration-square"></div>
        </div>
        
        <div class="hero-right">
          <!-- Área del Logo -->
          <div class="signal-map" aria-hidden="true">
            <div class="signal-ring ring-one"></div>
            <div class="signal-ring ring-two"></div>
            <div class="signal-node node-one"></div>
            <div class="signal-node node-two"></div>
            <div class="signal-node node-three"></div>
            <div class="signal-line line-one"></div>
            <div class="signal-line line-two"></div>
          </div>
          
          <button class="scroll-down-btn" @click="scrollToBottom">
            ↓
          </button>
        </div>
      </section>

      <!-- Sección inferior: diseño de dos columnas -->
      <section v-if="false" class="insight-strip">
        <article class="insight-card">
          <span class="insight-num">01</span>
          <h3>{{ $t('home.howItWorksTitle') }}</h3>
          <p>{{ $t('home.howItWorksDesc') }}</p>
        </article>
        <article class="insight-card">
          <span class="insight-num">02</span>
          <h3>{{ $t('home.workflowPreviewTitle') }}</h3>
          <p>{{ $t('home.workflowPreviewDesc') }}</p>
        </article>
        <article class="insight-card">
          <span class="insight-num">03</span>
          <h3>{{ $t('home.whyChooseTitle') }}</h3>
          <p>{{ $t('home.whyChooseDesc') }}</p>
        </article>
      </section>

      <section v-if="!activeInfoPanel" class="dashboard-section">
        <div class="dashboard-layout" :class="{ 'with-projects': isAuthenticated }">
        <ProjectSidebar v-if="isAuthenticated" embedded class="home-project-sidebar" />

        <!-- Columna izquierda: estado y pasos -->
        <div v-if="false" class="left-panel">
          <div class="panel-header">
            <span class="status-dot">■</span> {{ $t('home.systemStatus') }}
          </div>
          
          <h2 class="section-title">{{ $t('home.systemReady') }}</h2>
          <p class="section-desc">
            {{ $t('home.systemReadyDesc') }}
          </p>
          
          <!-- Tarjetas de métricas de datos -->
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-value">{{ $t('home.metricLowCost') }}</div>
              <div class="metric-label">{{ $t('home.metricLowCostDesc') }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ $t('home.metricHighAvail') }}</div>
              <div class="metric-label">{{ $t('home.metricHighAvailDesc') }}</div>
            </div>
          </div>

          <!-- Introducción de pasos de simulación del proyecto (nueva área) -->
          <div class="steps-container">
            <div class="steps-header">
               <span class="diamond-icon">◇</span> {{ $t('home.workflowSequence') }}
            </div>
            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step01Title') }}</div>
                  <div class="step-desc">{{ $t('home.step01Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step02Title') }}</div>
                  <div class="step-desc">{{ $t('home.step02Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step03Title') }}</div>
                  <div class="step-desc">{{ $t('home.step03Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step04Title') }}</div>
                  <div class="step-desc">{{ $t('home.step04Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">05</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step05Title') }}</div>
                  <div class="step-desc">{{ $t('home.step05Desc') }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Columna derecha: consola de interacción -->
        <div class="right-panel">
          <div class="console-box">
            <!-- Área de carga -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.realitySeed') }}</span>
                <span class="console-meta">{{ $t('home.supportedFormats') }}</span>
              </div>
              
              <div 
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt"
                  @change="handleFileSelect"
                  style="display: none"
                  :disabled="loading"
                />
                
                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">{{ $t('home.dragToUpload') }}</div>
                  <div class="upload-hint">{{ $t('home.orBrowse') }}</div>
                </div>
                
                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Línea divisoria -->
            <div class="console-divider">
              <span>{{ $t('home.inputParams') }}</span>
            </div>

            <!-- Área de entrada -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.simulationPrompt') }}</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  :placeholder="$t('home.promptPlaceholder')"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">{{ $t('home.engineBadge') }}</div>
              </div>
            </div>

            <!-- Botón de inicio -->
            <div class="console-section btn-section">
              <button 
                class="start-engine-btn"
                @click="handleStartSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">{{ $t('home.startEngine') }}</span>
                <span v-else>{{ $t('home.initializing') }}</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </div>
        </div>
      </section>

    </div>
    </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { availableLocales } from '@/i18n'
import ProjectSidebar from '../components/ProjectSidebar.vue'
import { getPendingUpload, setPendingUpload } from '../store/pendingUpload'
import { initializeAuthSession, useAuthSession } from '../store/authSession'

const router = useRouter()
const { locale, t } = useI18n({ useScope: 'global' })
const { state, isAuthenticated } = useAuthSession()
const hasChosenLanguage = ref(localStorage.getItem('youworld:languageSelected') === 'true')
const showIntro = ref(true)
const introLocales = computed(() => availableLocales.filter(item => ['es', 'en'].includes(item.key)))
const activeInfoPanel = ref(null)
const authCtaLabel = computed(() => {
  if (state.user?.name) return state.user.name
  if (state.user?.email) return state.user.email
  return t('auth.cta')
})

const infoTabs = computed(() => [
  { key: 'how', label: t('home.howItWorksTitle') },
  { key: 'workflow', label: t('home.workflowPreviewTitle') },
  { key: 'why', label: t('home.whyChooseTitle') }
])

const workflowDetails = computed(() => [
  { title: t('home.step01Title'), desc: t('home.step01Desc') },
  { title: t('home.step02Title'), desc: t('home.step02Desc') },
  { title: t('home.step03Title'), desc: t('home.step03Desc') },
  { title: t('home.step04Title'), desc: t('home.step04Desc') },
  { title: t('home.step05Title'), desc: t('home.step05Desc') }
])

const howParagraphs = computed(() => [
  t('home.howParagraph1'),
  t('home.howParagraph2'),
  t('home.howParagraph3')
])

const whyParagraphs = computed(() => [
  t('home.whyParagraph1'),
  t('home.whyParagraph2'),
  t('home.whyParagraph3')
])

const activeInfoContent = computed(() => {
  if (activeInfoPanel.value === 'workflow') {
    return { title: t('home.workflowPreviewTitle'), body: t('home.workflowPreviewDesc') }
  }
  if (activeInfoPanel.value === 'why') {
    return { title: t('home.whyChooseTitle'), body: t('home.whyChooseDesc') }
  }
  return { title: t('home.howItWorksTitle'), body: t('home.howItWorksDesc') }
})

const toggleInfoPanel = (key) => {
  activeInfoPanel.value = activeInfoPanel.value === key ? null : key
}

const chooseLanguage = (localeKey) => {
  locale.value = localeKey
  localStorage.setItem('locale', localeKey)
  localStorage.setItem('youworld:languageSelected', 'true')
  document.documentElement.lang = localeKey
  hasChosenLanguage.value = true
  showIntro.value = false
}

onMounted(() => {
  initializeAuthSession()

  const pending = getPendingUpload()
  if (pending.isPending) {
    files.value = pending.files
    formData.value.simulationRequirement = pending.simulationRequirement
  }

  if (hasChosenLanguage.value) {
    window.setTimeout(() => {
      showIntro.value = false
    }, 1800)
  }
})

// Datos del formulario
const formData = ref({
  simulationRequirement: ''
})

// Lista de archivos
const files = ref([])

const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)

// Referencia de entrada de archivo
const fileInput = ref(null)

// Propiedad computada: si se puede enviar
const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

// Activar selección de archivo
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// Procesar selección de archivo
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// procesar arrastre
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return
  
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// agregar archivos
const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

// quitar archivo
const removeFile = (index) => {
  files.value.splice(index, 1)
}

// scroll abajo
const scrollToBottom = () => {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  })
}

const openAuthGate = () => {
  if (files.value.length > 0 || formData.value.simulationRequirement.trim()) {
    setPendingUpload(files.value, formData.value.simulationRequirement)
  }
  router.push({ name: 'Auth' })
}

const handleStartSimulation = () => {
  if (!canSubmit.value || loading.value) return

  setPendingUpload(files.value, formData.value.simulationRequirement)

  if (!isAuthenticated.value) {
    router.push({
      name: 'Auth',
      query: { next: 'process-new' }
    })
    return
  }

  router.push({
    name: 'Process',
    params: { projectId: 'new' }
  })
}

// Iniciar simulación - navegación inmediata, la llamada API se hace en la página Process
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  
  // almacenar datos pendientes de subir
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    
    // navegación a la página Process (usar identificador especial para nuevo proyecto)
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
/* Variables globales y reset */
:root {
  --black: #000000;
  --white: #FFFFFF;
  --orange: #FF4500;
  --gray-light: #F5F5F5;
  --gray-text: #666666;
  --border: #E5E5E5;
  /* 
    Usar Space Grotesk como fuente principal para títulos, JetBrains Mono para código/etiquetas
    Asegurar que estas Google Fonts estén importadas en index.html 
  */
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  --font-cn: 'Noto Sans SC', system-ui, sans-serif;
}

.home-container {
  min-height: 100vh;
  background: var(--white);
  font-family: var(--font-sans);
  color: var(--black);
}

/* Barra de navegación superior */
.navbar {
  height: 60px;
  background: var(--black);
  color: var(--white);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.github-link {
  color: var(--white);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.github-link:hover {
  opacity: 0.8;
}

.arrow {
  font-family: sans-serif;
}

/* Área de contenido principal */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

/* Área Hero */
.hero-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 80px;
  position: relative;
}

.hero-left {
  flex: 1;
  padding-right: 60px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.orange-tag {
  background: var(--orange);
  color: var(--white);
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.75rem;
}

.version-text {
  color: #999;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.main-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 500;
  margin: 0 0 40px 0;
  letter-spacing: -2px;
  color: var(--black);
}

.gradient-text {
  background: linear-gradient(90deg, #000000 0%, #444444 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-desc {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--gray-text);
  max-width: 640px;
  margin-bottom: 50px;
  font-weight: 400;
  text-align: justify;
}

.hero-desc p {
  margin-bottom: 1.5rem;
}

.highlight-bold {
  color: var(--black);
  font-weight: 700;
}

.highlight-orange {
  color: var(--orange);
  font-weight: 700;
  font-family: var(--font-mono);
}

.highlight-code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  color: var(--black);
  font-weight: 600;
}

.slogan-text {
  font-size: 1.2rem;
  font-weight: 520;
  color: var(--black);
  letter-spacing: 1px;
  border-left: 3px solid var(--orange);
  padding-left: 15px;
  margin-top: 20px;
}

.blinking-cursor {
  color: var(--orange);
  animation: blink 1s step-end infinite;
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.decoration-square {
  width: 16px;
  height: 16px;
  background: var(--orange);
}

.hero-right {
  flex: 0.8;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}

.logo-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-right: 40px;
}

.hero-logo {
  max-width: 500px; /* ajustar tamaño del logo */
  width: 100%;
}

.scroll-down-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--orange);
  font-size: 1.2rem;
  transition: all 0.2s;
}

.scroll-down-btn:hover {
  border-color: var(--orange);
}

/* Dashboard diseño de dos columnas */
.dashboard-section {
  display: flex;
  gap: 60px;
  border-top: 1px solid var(--border);
  padding-top: 60px;
  align-items: flex-start;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  display: flex;
  flex-direction: column;
}

/* Panel izquierdo */
.left-panel {
  flex: 0.8;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  color: var(--orange);
  font-size: 0.8rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 520;
  margin: 0 0 15px 0;
}

.section-desc {
  color: var(--gray-text);
  margin-bottom: 25px;
  line-height: 1.6;
}

.metrics-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.metric-card {
  border: 1px solid var(--border);
  padding: 20px 30px;
  min-width: 150px;
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 520;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.85rem;
  color: #999;
}

/* Introducción a pasos de simulación del proyecto */
.steps-container {
  border: 1px solid var(--border);
  padding: 30px;
  position: relative;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--black);
  opacity: 0.3;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 520;
  font-size: 1rem;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: var(--gray-text);
}

/* Panel derecho: consola de interacción */
.right-panel {
  flex: 1.2;
}

.console-box {
  border: 1px solid #CCC; /* borde externo sólido */
  padding: 8px; /* padding interno para efecto de doble borde */
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
}

.upload-zone {
  border: 1px dashed #CCC;
  height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover {
  background: #F0F0F0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #999;
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #EEE;
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid #DDD;
  background: #FAFAFA;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #AAA;
}

.start-engine-btn {
  width: 100%;
  background: var(--black);
  color: var(--white);
  border: none;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

/* Estado clickeable (no disabled) */
.start-engine-btn:not(:disabled) {
  background: var(--black);
  border: 1px solid var(--black);
  animation: pulse-border 2s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  transform: none;
  border: 1px solid #E5E5E5;
}

/* Animación guía: pulso sutil del borde */
@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(0, 0, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
}

/* YouWorld redesign */
.home-container {
  --yw-bg: #080414;
  --yw-bg-2: #14072b;
  --yw-surface: rgba(255, 255, 255, 0.075);
  --yw-line: rgba(221, 196, 255, 0.2);
  --yw-text: #f6efff;
  --yw-muted: #b9a9ce;
  --yw-accent: #ff7a1a;
  --yw-cyan: #72f6ff;
  min-height: 100vh;
  color: var(--yw-text);
  background:
    radial-gradient(circle at 12% 12%, rgba(113, 25, 185, 0.55), transparent 34%),
    radial-gradient(circle at 82% 20%, rgba(255, 122, 26, 0.22), transparent 28%),
    linear-gradient(135deg, var(--yw-bg), var(--yw-bg-2) 58%, #05020b);
  overflow-x: hidden;
}

.home-container::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.75), transparent 85%);
}

.intro-screen {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
  position: relative;
  isolation: isolate;
}

.intro-grid {
  position: absolute;
  inset: 7%;
  border: 1px solid var(--yw-line);
  background:
    linear-gradient(90deg, transparent 49%, rgba(114, 246, 255, 0.12) 50%, transparent 51%),
    linear-gradient(transparent 49%, rgba(255, 122, 26, 0.12) 50%, transparent 51%);
  background-size: 86px 86px;
  opacity: 0.65;
  transform: perspective(900px) rotateX(62deg);
  transform-origin: center bottom;
}

.intro-shell {
  width: min(920px, 100%);
  padding: clamp(32px, 7vw, 76px);
  border: 1px solid var(--yw-line);
  background: linear-gradient(145deg, rgba(20, 7, 43, 0.78), rgba(8, 4, 20, 0.93));
  box-shadow: 0 30px 120px rgba(0, 0, 0, 0.52), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  position: relative;
}

.intro-shell::before {
  content: '';
  position: absolute;
  inset: -1px auto auto -1px;
  width: 42%;
  height: 3px;
  background: linear-gradient(90deg, var(--yw-accent), var(--yw-cyan));
}

.intro-eyebrow,
.orange-tag,
.version-text,
.console-label,
.panel-header,
.steps-header,
.insight-num,
.intro-action-label {
  color: var(--yw-cyan);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

.intro-title {
  margin: 18px 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(3.5rem, 12vw, 9rem);
  line-height: 0.88;
  letter-spacing: -0.08em;
  text-shadow: 0 0 42px rgba(114, 246, 255, 0.18);
}

.intro-copy {
  max-width: 720px;
  color: var(--yw-muted);
  font-size: clamp(1.05rem, 2vw, 1.45rem);
  line-height: 1.65;
}

.intro-actions {
  margin-top: 42px;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.intro-language-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.intro-language-btn,
.github-link {
  border: 1px solid var(--yw-line);
  background: rgba(255, 255, 255, 0.08);
  color: var(--yw-text);
}

.intro-language-btn {
  padding: 14px 22px;
  min-width: 128px;
  cursor: pointer;
  font-family: var(--font-mono);
  font-weight: 800;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.intro-language-btn:hover {
  transform: translateY(-3px);
  border-color: var(--yw-cyan);
  background: rgba(114, 246, 255, 0.12);
}

.navbar {
  height: 76px;
  padding: 0 5vw;
  background: rgba(8, 4, 20, 0.72);
  border-bottom: 1px solid var(--yw-line);
  backdrop-filter: blur(18px);
}

.nav-brand {
  color: var(--yw-text);
  letter-spacing: 0.14em;
  text-shadow: 0 0 28px rgba(114, 246, 255, 0.25);
}

.github-link {
  padding: 11px 16px;
  text-decoration: none;
}

.main-content {
  max-width: 1440px;
  padding: 64px 5vw 90px;
  margin: 0 auto;
}

.hero-section {
  min-height: auto;
  padding: 34px 0 26px;
  align-items: stretch;
  gap: 48px;
}

.hero-left {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.035));
  border: 1px solid var(--yw-line);
  padding: clamp(30px, 5vw, 56px);
  position: relative;
}

.hero-left::after,
.right-panel::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  border: 1px solid rgba(255, 122, 26, 0.16);
  transform: translate(10px, 10px);
}

.main-title {
  color: var(--yw-text);
  font-size: clamp(2.8rem, 6vw, 6rem);
  line-height: 0.96;
  letter-spacing: -0.07em;
}

.gradient-text {
  background: linear-gradient(90deg, #ffffff, #b083ff 45%, var(--yw-accent));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-desc {
  color: var(--yw-muted);
  font-size: 1.05rem;
}

.highlight-bold,
.highlight-orange,
.highlight-code {
  color: #fff;
  background: rgba(255, 122, 26, 0.14);
}

.hero-right {
  display: grid;
  place-items: center;
  min-height: 360px;
}

.signal-map {
  width: min(430px, 80vw);
  aspect-ratio: 1;
  position: relative;
  border: 1px solid var(--yw-line);
  background:
    radial-gradient(circle at center, rgba(114, 246, 255, 0.18), transparent 24%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02));
  box-shadow: inset 0 0 80px rgba(114, 246, 255, 0.08), 0 28px 90px rgba(0, 0, 0, 0.38);
}

.signal-ring,
.signal-node,
.signal-line {
  position: absolute;
}

.signal-ring {
  inset: 18%;
  border: 1px solid rgba(114, 246, 255, 0.3);
  transform: rotate(45deg);
}

.ring-two {
  inset: 33%;
  border-color: rgba(255, 122, 26, 0.35);
}

.signal-node {
  width: 13px;
  height: 13px;
  background: var(--yw-cyan);
  box-shadow: 0 0 24px var(--yw-cyan);
}

.node-one { top: 24%; left: 28%; }
.node-two { right: 23%; top: 38%; background: var(--yw-accent); box-shadow: 0 0 24px var(--yw-accent); }
.node-three { left: 47%; bottom: 22%; }

.signal-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(114, 246, 255, 0.75), transparent);
  transform-origin: left center;
}

.line-one { width: 58%; left: 25%; top: 42%; transform: rotate(18deg); }
.line-two { width: 44%; left: 33%; bottom: 34%; transform: rotate(-34deg); }

.scroll-down-btn {
  border-color: var(--yw-line);
  color: var(--yw-text);
  background: rgba(255, 255, 255, 0.08);
}

.insight-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin: 8px 0 32px;
}

.insight-card,
.left-panel,
.right-panel,
.console-box {
  border: 1px solid var(--yw-line);
  background: rgba(10, 5, 24, 0.72);
  box-shadow: 0 20px 70px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(16px);
}

.insight-card {
  padding: 24px;
}

.insight-card h3 {
  margin: 10px 0 8px;
  color: var(--yw-text);
  font-size: 1.18rem;
}

.insight-card p,
.section-desc,
.metric-label,
.step-desc,
.console-meta,
.upload-hint {
  color: var(--yw-muted);
}

.dashboard-section {
  gap: 28px;
}

.left-panel,
.right-panel {
  padding: 30px;
  position: relative;
}

.section-title,
.metric-value,
.step-title,
.upload-title {
  color: var(--yw-text);
}

.metric-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--yw-line);
}

.workflow-item {
  border-bottom-color: var(--yw-line);
}

.step-num {
  color: var(--yw-cyan);
}

.console-box {
  padding: 28px;
}

.upload-zone,
.input-wrapper {
  background: rgba(255, 255, 255, 0.045);
  border-color: var(--yw-line);
}

.upload-zone:hover,
.upload-zone.drag-over {
  background: rgba(114, 246, 255, 0.08);
  border-color: var(--yw-cyan);
}

.upload-icon {
  border-color: var(--yw-line);
  color: var(--yw-cyan);
}

.file-item {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--yw-line);
  color: var(--yw-text);
}

.code-input {
  color: var(--yw-text);
}

.code-input::placeholder {
  color: rgba(246, 239, 255, 0.44);
}

.model-badge {
  color: var(--yw-cyan);
}

.start-engine-btn:not(:disabled) {
  background: linear-gradient(90deg, #7c2cff, var(--yw-accent));
  border: 1px solid rgba(255, 255, 255, 0.22);
}

.start-engine-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, var(--yw-accent), #ffcf70);
  color: #12051f;
}

.start-engine-btn:disabled {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(246, 239, 255, 0.42);
  border-color: var(--yw-line);
}

/* Adaptación responsive */
@media (max-width: 1024px) {
  .insight-strip {
    grid-template-columns: 1fr;
  }

  .dashboard-section {
    flex-direction: column;
  }
  
  .hero-section {
    flex-direction: column;
  }
  
  .hero-left {
    padding-right: 0;
    margin-bottom: 40px;
  }
  
  .hero-logo {
    max-width: 200px;
    margin-bottom: 20px;
  }
}
/* YouWorld refined pass */
.home-container {
  background:
    radial-gradient(circle at 72% 12%, rgba(91, 203, 190, 0.24), transparent 30%),
    radial-gradient(circle at 28% 10%, rgba(77, 35, 111, 0.34), transparent 34%),
    linear-gradient(125deg, #050607 0%, #081310 32%, #0b0715 72%, #05020a 100%);
  font-family: 'Inter', sans-serif;
}

.home-container::before,
.intro-grid,
.hero-section,
.insight-strip,
.left-panel {
  display: none;
}

.intro-screen {
  padding: 24px;
}

.intro-auth-link {
  position: absolute;
  top: 28px;
  right: clamp(18px, 5vw, 52px);
  z-index: 2;
  border: 0;
  border-radius: 999px;
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(244, 255, 251, 0.88);
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  transition: background 0.2s ease, color 0.2s ease;
}

.intro-shell {
  width: min(720px, 100%);
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  text-align: center;
}

.intro-shell::before {
  display: none;
}

.intro-eyebrow {
  font-size: 0.72rem;
  letter-spacing: 0.22em;
  color: rgba(114, 246, 255, 0.72);
}

.intro-title {
  margin: 18px 0 16px;
  font-family: 'Inter', sans-serif;
  font-size: clamp(2.5rem, 7vw, 4.8rem);
  letter-spacing: -0.08em;
  font-weight: 700;
  text-shadow: none;
}

.intro-copy {
  margin: 0 auto;
  max-width: 620px;
  font-size: clamp(1rem, 1.8vw, 1.22rem);
  line-height: 1.72;
  color: rgba(246, 239, 255, 0.72);
}

.intro-actions {
  margin-top: 34px;
  justify-content: center;
  gap: 14px;
}

.intro-action-label {
  width: 100%;
  color: rgba(246, 239, 255, 0.52);
  font-size: 0.74rem;
}

.intro-language-btn {
  min-width: 118px;
  padding: 12px 18px;
  border-radius: 999px;
  background: rgba(115, 220, 209, 0.18);
  border: 0;
  color: #eafffb;
  box-shadow: none;
  font-family: 'Inter', sans-serif;
}

.intro-language-btn:hover {
  transform: translateY(-1px);
  background: rgba(115, 220, 209, 0.28);
}

.navbar {
  height: auto;
  padding: 26px clamp(18px, 5vw, 64px) 0;
  background: transparent;
  border: 0;
  backdrop-filter: none;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: clamp(22px, 4vw, 56px);
  min-width: 0;
}

.nav-brand {
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
  color: rgba(235, 255, 251, 0.92);
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  text-shadow: none;
  white-space: nowrap;
}

.nav-info-tabs {
  display: flex;
  align-items: center;
  gap: clamp(18px, 3vw, 38px);
}

.nav-info-tab {
  padding: 0;
  border: 0;
  background: transparent;
  color: rgba(235, 255, 251, 0.58);
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  transition: color 0.2s ease;
}

.nav-info-tab:hover,
.nav-info-tab.active {
  color: #77ddd5;
}

.nav-links {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.nav-auth-btn {
  border: 0;
  border-radius: 999px;
  padding: 11px 18px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(244, 255, 251, 0.88);
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-auth-btn:hover,
.intro-auth-link:hover {
  background: rgba(119, 221, 213, 0.16);
  color: #f4fffb;
}

.main-content {
  width: 100%;
  max-width: none;
  padding: clamp(20px, 3vw, 34px) clamp(30px, 4vw, 56px) 72px;
}

.section-page {
  max-width: 860px;
  min-height: calc(100vh - 120px);
  margin: 0 auto;
  padding: clamp(10px, 2vw, 24px) 0 56px;
}

.section-back {
  border: 0;
  background: transparent;
  color: rgba(235, 255, 251, 0.58);
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  font-size: 0.84rem;
  padding: 0;
  margin-bottom: clamp(22px, 3vw, 34px);
}

.section-back:hover {
  color: #f6efff;
}

.section-kicker {
  margin: 0 0 14px;
  color: rgba(119, 221, 213, 0.78);
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.section-page h1 {
  margin: 0 0 22px;
  color: #f4fffb;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: clamp(2.2rem, 5vw, 4.2rem);
  line-height: 1;
  letter-spacing: -0.06em;
}

.section-body {
  max-width: 720px;
  margin: 0;
  color: rgba(235, 255, 251, 0.68);
  font-size: 1.08rem;
  line-height: 1.78;
}

.section-split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 360px);
  gap: clamp(28px, 5vw, 58px);
  align-items: start;
}

.section-copy {
  display: grid;
  gap: 18px;
}

.section-copy.wide {
  max-width: 780px;
}

.section-copy p {
  margin: 0;
  color: rgba(235, 255, 251, 0.68);
  font-size: 1.05rem;
  line-height: 1.76;
}

.world-preview-placeholder {
  min-height: 320px;
  border-radius: 28px;
  background:
    radial-gradient(circle at 24% 18%, rgba(119, 221, 213, 0.18), transparent 32%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.025));
  display: grid;
  place-items: center;
  color: rgba(235, 255, 251, 0.46);
  text-align: center;
  padding: 28px;
}

.section-steps {
  list-style: none;
  counter-reset: steps;
  padding: 0;
  margin: 28px 0 0;
  display: grid;
  gap: 24px;
}

.section-steps li {
  counter-increment: steps;
  position: relative;
  padding-left: 56px;
}

.section-steps li::before {
  content: counter(steps, decimal-leading-zero);
  position: absolute;
  left: 0;
  top: 2px;
  color: rgba(119, 221, 213, 0.72);
  font-family: 'Inter', sans-serif;
  font-weight: 800;
}

.section-steps span {
  display: block;
  color: #f4fffb;
  font-weight: 800;
  font-size: 1.08rem;
  margin-bottom: 6px;
}

.section-steps p {
  margin: 0;
  color: rgba(235, 255, 251, 0.62);
  line-height: 1.65;
}

.info-panel {
  margin: 0 0 28px;
}

.info-panel-inner {
  position: relative;
  padding: 24px 28px;
  border: 1px solid rgba(221, 196, 255, 0.16);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.045);
}

.info-panel h2 {
  margin: 0 0 10px;
  font-size: 1.05rem;
  color: #f6efff;
}

.info-panel p,
.info-steps {
  margin: 0;
  color: rgba(246, 239, 255, 0.7);
  line-height: 1.7;
}

.info-steps {
  padding-left: 20px;
}

.info-steps li + li {
  margin-top: 8px;
}

.info-close {
  position: absolute;
  top: 12px;
  right: 14px;
  border: 0;
  background: transparent;
  color: rgba(246, 239, 255, 0.52);
  cursor: pointer;
  font-size: 1.2rem;
}

.dashboard-section {
  display: block;
  padding-top: 0;
  border-top: 0;
}

.dashboard-layout {
  display: block;
}

.dashboard-layout.with-projects {
  display: grid;
  grid-template-columns: 320px minmax(780px, 1fr);
  gap: 36px;
  align-items: start;
}

.home-project-sidebar {
  position: sticky;
  top: 92px;
  align-self: start;
}

.right-panel {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.right-panel::after {
  display: none;
}

.console-box {
  border-radius: 18px;
  background: transparent;
  border: 0;
  box-shadow: none;
  backdrop-filter: none;
  padding: 0;
  width: 100%;
}

.upload-zone,
.input-wrapper,
.start-engine-btn,
.metric-card {
  border-radius: 22px;
}

.upload-zone {
  height: 265px;
  background: rgba(255, 255, 255, 0.045);
  border: 0;
  box-shadow: inset 0 0 0 1px rgba(235, 255, 251, 0.08);
}

.input-wrapper {
  background: rgba(255, 255, 255, 0.045);
  border: 0;
  box-shadow: inset 0 0 0 1px rgba(235, 255, 251, 0.08);
  min-height: 182px;
}

.start-engine-btn {
  overflow: hidden;
  border: 0;
  font-family: 'Inter', sans-serif;
}

.console-label,
.console-meta,
.console-divider span,
.model-badge,
.upload-title,
.upload-hint,
.code-input,
.file-item {
  font-family: 'Inter', sans-serif;
}

.console-label,
.model-badge {
  color: #77ddd5;
  letter-spacing: 0.08em;
}

.console-meta,
.console-divider span,
.upload-hint {
  color: rgba(235, 255, 251, 0.46);
}

.console-divider::before,
.console-divider::after {
  background: rgba(235, 255, 251, 0.12);
}

.upload-icon {
  border: 0;
  background: rgba(119, 221, 213, 0.12);
  color: #77ddd5;
  border-radius: 14px;
}

.upload-title {
  color: rgba(244, 255, 251, 0.88);
}

.code-input {
  color: rgba(244, 255, 251, 0.9);
  font-weight: 500;
}

.start-engine-btn:not(:disabled) {
  background: linear-gradient(90deg, #78ddd5, #a7eee8);
  color: #06100f;
}

.start-engine-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #a7eee8, #78ddd5);
  color: #06100f;
}

.screen-flow-enter-active,
.screen-flow-leave-active {
  transition: opacity 0.55s ease, transform 0.55s ease, filter 0.55s ease;
}

.screen-flow-enter-from {
  opacity: 0;
  transform: translateY(18px) scale(0.985);
  filter: blur(8px);
}

.screen-flow-leave-to {
  opacity: 0;
  transform: translateY(-14px) scale(1.015);
  filter: blur(8px);
}

@media (max-width: 720px) {
  .section-split {
    grid-template-columns: 1fr;
  }

  .dashboard-layout.with-projects {
    grid-template-columns: 1fr;
  }

  .home-project-sidebar {
    position: static;
  }

  .world-preview-placeholder {
    min-height: 220px;
  }

  .navbar {
    height: auto;
    align-items: flex-start;
    padding-top: 16px;
    padding-bottom: 16px;
    gap: 14px;
  }

  .nav-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .nav-info-tabs {
    flex-wrap: wrap;
    gap: 12px 18px;
  }

  .nav-links {
    margin-left: auto;
  }

  .intro-auth-link {
    top: 18px;
  }
}
</style>

<style>
/* English locale adjustments (unscoped to target html[lang]) */
html[lang="en"] .main-title {
  font-size: 3.5rem;
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: -1px;
}

html[lang="en"] .hero-desc {
  text-align: left;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0;
}

html[lang="en"] .slogan-text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: 0;
}

html[lang="en"] .tag-row {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .navbar .nav-links {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Left pane: system status + workflow */
html[lang="en"] .status-section {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .status-section .status-ready {
  font-size: 1.6rem;
}

html[lang="en"] .status-section .metric-value {
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1.4rem;
}

html[lang="en"] .workflow-list .step-title {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .workflow-list .step-desc {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  font-size: 0.72rem !important;
  line-height: 1.4 !important;
}

html[lang="en"] .workflow-list {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
