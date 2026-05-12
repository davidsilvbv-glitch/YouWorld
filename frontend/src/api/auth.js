import service from './index'

export const getCurrentUser = () => service.get('/api/auth/me')

export const loginWithGoogle = (credential) =>
  service.post('/api/auth/google', { credential })

export const logoutUser = () => service.post('/api/auth/logout')
