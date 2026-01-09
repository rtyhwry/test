import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isManager = computed(() => ['admin', 'manager'].includes(user.value?.role))
  
  async function login(credentials) {
    try {
      const response = await api.auth.login(credentials)
      token.value = response.data.access_token
      user.value = response.data.user
      localStorage.setItem('token', token.value)
      return response.data
    } catch (error) {
      throw error
    }
  }
  
  async function logout() {
    try {
      await api.auth.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
    }
  }
  
  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.users.me()
      user.value = response.data
    } catch (error) {
      console.error('Fetch user error:', error)
      logout()
    }
  }
  
  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    isManager,
    login,
    logout,
    fetchUser
  }
})
