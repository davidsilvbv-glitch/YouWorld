import axios from 'axios'
import i18n from '../i18n'

// Keep API calls relative to the current host and allow long ontology/graph jobs.
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 900000,
  headers: {
    'Content-Type': 'application/json'
  }
})

service.interceptors.request.use(
  config => {
    config.headers['Accept-Language'] = i18n.global.locale.value
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    const res = response.data

    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }

    return res
  },
  error => {
    console.error('Response error:', error)

    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
      return Promise.reject(new Error(i18n.global.t('common.timeout', 'Timeout')))
    }

    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
      return Promise.reject(
        new Error(i18n.global.t('common.networkError', 'Network Error'))
      )
    }

    let userMessage = i18n.global.t('common.serverError', 'Server error')
    if (error.response && error.response.data) {
      const resData = error.response.data
      if (resData.error) {
        userMessage = resData.error
      } else if (resData.message) {
        userMessage = resData.message
      }
    }

    return Promise.reject(new Error(userMessage))
  }
)

export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error

      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
