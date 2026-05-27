import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { authApi } from '@/services/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  // 初始化用户信息
  async function initUser() {
    if (token.value && !user.value) {
      try {
        const userData = await authApi.getCurrentUser()
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
      } catch (error) {
        console.error('获取用户信息失败:', error)
        logout()
      }
    } else if (localStorage.getItem('user')) {
      try {
        user.value = JSON.parse(localStorage.getItem('user') || 'null')
      } catch (error) {
        console.error('解析用户信息失败:', error)
      }
    }
  }

  // 登录
  async function login(username: string, password: string) {
    try {
      loading.value = true
      const response = await authApi.login({ username, password })
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      // 登录成功后获取用户信息
      const userData = await authApi.getCurrentUser()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  async function register(username: string, email: string, password: string) {
    try {
      loading.value = true
      await authApi.register({ username, email, password })
      // 注册成功后自动登录
      const loginResult = await login(username, password)
      if (loginResult) {
        ElMessage.success('注册成功')
      }
      return loginResult
    } catch (error) {
      console.error('注册失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  function logout() {
    token.value = null
    user.value = null
    authApi.logout()
    ElMessage.success('已退出登录')
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    initUser,
    login,
    register,
    logout,
  }
})
