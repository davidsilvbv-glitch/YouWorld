import { computed, reactive } from 'vue'
import { getCurrentUser, logoutUser } from '../api/auth'

const state = reactive({
  user: null,
  initialized: false,
  loading: false
})

export const isAuthenticated = computed(() => !!state.user)

export async function initializeAuthSession(force = false) {
  if (state.loading) return state.user
  if (state.initialized && !force) return state.user

  state.loading = true
  try {
    const res = await getCurrentUser()
    state.user = res?.data || null
    state.initialized = true
    return state.user
  } catch (error) {
    state.user = null
    state.initialized = true
    return null
  } finally {
    state.loading = false
  }
}

export async function clearAuthSession() {
  try {
    await logoutUser()
  } catch (error) {
    console.warn('Logout failed:', error)
  } finally {
    state.user = null
    state.initialized = true
  }
}

export function useAuthSession() {
  return {
    state,
    isAuthenticated
  }
}
