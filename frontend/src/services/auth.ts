import { api } from './api'
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types/user'

export const authApi = {
  // 登录
  login(data: LoginRequest): Promise<AuthResponse> {
    return api.post<AuthResponse>('/auth/login', data)
  },

  // 注册
  register(data: RegisterRequest): Promise<User> {
    return api.post<User>('/auth/register', data)
  },

  // 获取当前用户信息
  getCurrentUser(): Promise<User> {
    return api.get<User>('/auth/me')
  },

  // 登出
  logout(): void {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },
}
