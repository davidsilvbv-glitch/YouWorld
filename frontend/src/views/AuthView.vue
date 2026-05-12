<template>
  <div class="auth-view">
    <header class="auth-header">
      <button class="brand" @click="goHome">YOUWORLD</button>
      <button class="back-link" @click="goHome">{{ $t('common.back') }}</button>
    </header>

    <main class="auth-main">
      <section class="auth-shell">
        <p class="auth-kicker">{{ $t('auth.screenEyebrow') }}</p>
        <h1 class="auth-title">
          {{ state.user ? $t('auth.welcomeTitle') : $t('auth.title') }}
        </h1>
        <p class="auth-copy">
          {{ state.user ? $t('auth.loggedInText') : descriptionText }}
        </p>

        <div v-if="state.loading" class="auth-status-card">
          <span class="spinner"></span>
          <span>{{ $t('auth.loadingSession') }}</span>
        </div>

        <div v-else-if="state.user" class="auth-status-card session-card">
          <div class="session-avatar">
            {{ userInitial }}
          </div>
          <div class="session-copy">
            <span class="session-label">{{ $t('auth.loggedInAs') }}</span>
            <strong>{{ state.user.name || state.user.email }}</strong>
            <span>{{ state.user.email }}</span>
          </div>
        </div>

        <div v-else class="auth-actions">
          <div ref="googleButtonHost" class="google-button-host"></div>
          <button
            v-if="!googleButtonRendered"
            class="google-fallback-btn"
            :disabled="!googleClientId || signingIn"
            @click="promptGoogleSignIn"
          >
            <span v-if="signingIn">{{ $t('common.loading') }}</span>
            <span v-else>{{ $t('auth.googleButton') }}</span>
          </button>
          <p class="auth-helper">
            {{ googleClientId ? $t('auth.helper') : $t('auth.googleUnavailable') }}
          </p>
        </div>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <div class="auth-footer-actions">
          <button class="primary-action" @click="handleContinue" :disabled="!state.user">
            {{ continueLabel }}
          </button>
          <button
            v-if="state.user"
            class="secondary-action"
            @click="handleLogout"
          >
            {{ $t('auth.logout') }}
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { loginWithGoogle } from '../api/auth'
import { getPendingUpload } from '../store/pendingUpload'
import { clearAuthSession, initializeAuthSession, useAuthSession } from '../store/authSession'

const router = useRouter()
const route = useRoute()
const { t } = useI18n({ useScope: 'global' })
const { state } = useAuthSession()

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
const googleButtonHost = ref(null)
const googleButtonRendered = ref(false)
const signingIn = ref(false)
const errorMessage = ref('')

const pendingUpload = computed(() => getPendingUpload())
const hasPendingStart = computed(() => {
  return route.query.next === 'process-new' && pendingUpload.value.isPending
})

const descriptionText = computed(() => {
  return hasPendingStart.value
    ? t('auth.startRestriction')
    : t('auth.description')
})

const continueLabel = computed(() => {
  return hasPendingStart.value ? t('auth.continueToEngine') : t('auth.continueToHome')
})

const userInitial = computed(() => {
  const source = state.user?.name || state.user?.email || 'Y'
  return source.charAt(0).toUpperCase()
})

const goHome = () => {
  router.push('/')
}

const continueAfterAuth = () => {
  if (hasPendingStart.value) {
    router.replace({
      name: 'Process',
      params: { projectId: 'new' }
    })
    return
  }
  router.replace('/')
}

const handleContinue = () => {
  if (!state.user) return
  continueAfterAuth()
}

const handleLogout = async () => {
  await clearAuthSession()
  errorMessage.value = ''
  await nextTick()
  renderGoogleButton()
}

const handleGoogleCredential = async (response) => {
  if (!response?.credential) {
    errorMessage.value = t('auth.googleCredentialMissing')
    return
  }

  signingIn.value = true
  errorMessage.value = ''

  try {
    await loginWithGoogle(response.credential)
    await initializeAuthSession(true)
    continueAfterAuth()
  } catch (error) {
    errorMessage.value = error.message || t('auth.sessionFailed')
  } finally {
    signingIn.value = false
  }
}

const renderGoogleButton = () => {
  if (!googleClientId || !googleButtonHost.value || !window.google?.accounts?.id) {
    googleButtonRendered.value = false
    return
  }

  googleButtonHost.value.innerHTML = ''
  window.google.accounts.id.initialize({
    client_id: googleClientId,
    callback: handleGoogleCredential
  })
  window.google.accounts.id.renderButton(googleButtonHost.value, {
    theme: 'outline',
    size: 'large',
    shape: 'pill',
    text: 'continue_with',
    width: 320
  })
  googleButtonRendered.value = true
}

const promptGoogleSignIn = () => {
  if (!window.google?.accounts?.id || !googleClientId) return
  window.google.accounts.id.prompt()
}

const waitForGoogleButton = (attempt = 0) => {
  if (renderGoogleButton(), googleButtonRendered.value) return
  if (attempt >= 20) return
  window.setTimeout(() => waitForGoogleButton(attempt + 1), 250)
}

onMounted(async () => {
  await initializeAuthSession()
  await nextTick()

  if (state.user && !hasPendingStart.value) {
    return
  }

  waitForGoogleButton()
})
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  color: #f6efff;
  background:
    radial-gradient(circle at 72% 10%, rgba(91, 203, 190, 0.2), transparent 30%),
    radial-gradient(circle at 18% 10%, rgba(77, 35, 111, 0.32), transparent 34%),
    linear-gradient(125deg, #050607 0%, #081310 34%, #0b0715 72%, #05020a 100%);
  font-family: 'Inter', sans-serif;
}

.auth-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28px clamp(18px, 5vw, 52px) 0;
}

.brand,
.back-link {
  border: 0;
  background: transparent;
  color: rgba(244, 255, 251, 0.86);
  cursor: pointer;
}

.brand {
  font-size: 0.96rem;
  font-weight: 800;
  letter-spacing: 0.34em;
}

.back-link {
  font-size: 0.9rem;
  font-weight: 600;
}

.auth-main {
  min-height: calc(100vh - 90px);
  display: grid;
  place-items: center;
  padding: 28px;
}

.auth-shell {
  width: min(720px, 100%);
  padding: clamp(28px, 5vw, 52px);
  border-radius: 32px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.03));
  box-shadow:
    inset 0 0 0 1px rgba(235, 255, 251, 0.1),
    0 28px 90px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(18px);
}

.auth-kicker {
  margin: 0 0 12px;
  color: rgba(119, 221, 213, 0.76);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.auth-title {
  margin: 0 0 18px;
  font-size: clamp(2.3rem, 5vw, 4.5rem);
  line-height: 0.96;
  letter-spacing: -0.06em;
}

.auth-copy {
  margin: 0;
  max-width: 620px;
  color: rgba(235, 255, 251, 0.68);
  font-size: 1.03rem;
  line-height: 1.74;
}

.auth-status-card,
.auth-actions {
  margin-top: 28px;
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: inset 0 0 0 1px rgba(235, 255, 251, 0.08);
}

.auth-status-card {
  display: flex;
  align-items: center;
  gap: 14px;
  color: rgba(244, 255, 251, 0.84);
}

.session-card {
  align-items: flex-start;
}

.session-avatar {
  width: 48px;
  height: 48px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: rgba(119, 221, 213, 0.14);
  color: #77ddd5;
  font-weight: 800;
  font-size: 1rem;
  flex-shrink: 0;
}

.session-copy {
  display: grid;
  gap: 4px;
}

.session-label,
.auth-helper {
  color: rgba(235, 255, 251, 0.5);
  font-size: 0.92rem;
}

.google-button-host {
  min-height: 44px;
}

.google-fallback-btn {
  min-width: 220px;
  padding: 13px 20px;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(90deg, #78ddd5, #a7eee8);
  color: #06100f;
  font-weight: 700;
  cursor: pointer;
}

.google-fallback-btn:disabled {
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(235, 255, 251, 0.42);
}

.auth-error {
  margin: 18px 0 0;
  color: #ffac8c;
}

.auth-footer-actions {
  margin-top: 26px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-action,
.secondary-action {
  padding: 13px 18px;
  border-radius: 999px;
  border: 0;
  font-weight: 700;
  cursor: pointer;
}

.primary-action {
  background: linear-gradient(90deg, #78ddd5, #a7eee8);
  color: #06100f;
}

.primary-action:disabled {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(235, 255, 251, 0.4);
  cursor: not-allowed;
}

.secondary-action {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(244, 255, 251, 0.82);
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid rgba(119, 221, 213, 0.2);
  border-top-color: #77ddd5;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 720px) {
  .auth-header {
    padding-top: 18px;
  }

  .auth-footer-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .primary-action,
  .secondary-action,
  .google-fallback-btn {
    width: 100%;
  }
}
</style>
