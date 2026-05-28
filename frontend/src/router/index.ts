import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/debug',
    name: 'Debug',
    component: () => import('@/views/Debug.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'agents',
        name: 'AgentList',
        component: () => import('@/views/AgentList.vue'),
        meta: { title: 'Agent列表' },
      },
      {
        path: 'agents/create',
        name: 'AgentCreate',
        component: () => import('@/views/AgentCreate.vue'),
        meta: { title: '创建Agent' },
      },
      {
        path: 'agents/:id/edit',
        name: 'AgentEdit',
        component: () => import('@/views/AgentCreate.vue'),
        props: true,
        meta: { title: '编辑Agent' },
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/Chat.vue'),
        meta: { title: '对话' },
      },
      {
        path: 'chat/:conversationId',
        name: 'ChatConversation',
        component: () => import('@/views/Chat.vue'),
        props: true,
        meta: { title: '对话详情' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 简化的路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  const title = to.meta.title as string
  document.title = title ? `${title} - E-AgentScope` : 'E-AgentScope'
  
  // 检查是否需要登录
  const requiresAuth = to.meta.requiresAuth !== false
  
  // 直接从 localStorage 检查 token（避免 Pinia 未初始化的问题）
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token
  
  if (requiresAuth && !isLoggedIn) {
    // 需要登录但未登录，跳转到登录页
    next('/login')
  } else if (!requiresAuth && isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    // 已登录但访问登录/注册页，跳转到首页
    next('/dashboard')
  } else if (requiresAuth && isLoggedIn) {
    // 需要登录且已登录，尝试初始化用户信息
    const userStore = useUserStore()
    if (!userStore.user) {
      try {
        await userStore.initUser()
      } catch (error) {
        console.error('初始化用户信息失败:', error)
      }
    }
    next()
  } else {
    next()
  }
})

export default router
