import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
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

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  const title = to.meta.title as string
  document.title = title ? `${title} - E-AgentScope` : 'E-AgentScope'
  
  // 初始化用户信息
  if (userStore.token && !userStore.user) {
    await userStore.initUser()
  }

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (!requiresAuth && userStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
