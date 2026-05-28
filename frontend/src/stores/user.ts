import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { authApi } from '@/services/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 初始化
  const token = ref<string | null>(localStorage.getItem('token'))
  
  // 尝试从 localStorage 恢复用户信息
  let savedUser = null
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      savedUser = JSON.parse(userStr)
    }
  } catch (e) {
    console.error('Failed to parse saved user:', e)
  }
  
  const user = ref<User | null>(savedUser)
  const loading = ref(false)

  // 计算属性：只要 token 存在就认为已登录
  const isLoggedIn = computed(() => !!token.value)

  // 初始化用户信息
  async function initUser() {
    if (!token.value) {
      return
    }
    
    if (!user.value) {
      try {
        const userData = await authApi.getCurrentUser()
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
      } catch (error: any) {
        console.error('获取用户信息失败:', error)
        // 如果是 401 错误，才清除 token
        if (error?.response?.status === 401) {
          logout()
        }
      }
    }
  }

  // 登录
  async function login(username: string, password: string) {
    try {
      loading.value = true
      
      // 1. 调用登录接口
      const response = await authApi.login({ username, password })
      
      // 2. 保存 token
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      
      // 3. 获取用户信息
      const userData = await authApi.getCurrentUser()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      
      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      console.error('登录失败:', error)
      ElMessage.error(error?.response?.data?.detail || '登录失败，请检查用户名和密码')
      
      // 清除可能残留的数据
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  async function register(username: string, email: string, password: string) {
    try {
      loading.value = true
      
      // 1. 注册
      await authApi.register({ username, email, password })
      
      // 2. 自动登录
      const success = await login(username, password)
      
      if (success) {
        ElMessage.success('注册成功')
      }
      
      return success
    } catch (error: any) {
      console.error('注册失败:', error)
      ElMessage.error(error?.response?.data?.detail || '注册失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
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
