<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>E-AgentScope</h1>
        <p>智能体管理平台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        class="login-form"
      >
        <el-form-item>
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const loginForm = reactive({
  username: '',
  password: '',
})

const loading = ref(false)

const handleLogin = async () => {
  console.log('handleLogin called', loginForm)
  
  if (!loginForm.username || !loginForm.password) {
    ElMessage.error('请输入用户名和密码')
    return
  }
  
  try {
    loading.value = true
    console.log('Calling login API...')
    
    // 直接调用登录 API
    const response = await axios.post('http://localhost:8000/api/auth/login', {
      username: loginForm.username,
      password: loginForm.password
    })
    
    console.log('Login response:', response.data)
    
    // 保存 token
    localStorage.setItem('token', response.data.access_token)
    console.log('Token saved to localStorage')
    
    // 获取用户信息
    const userResponse = await axios.get('http://localhost:8000/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${response.data.access_token}`
      }
    })
    
    console.log('User info:', userResponse.data)
    localStorage.setItem('user', JSON.stringify(userResponse.data))
    
    ElMessage.success('登录成功')
    
    // 跳转到首页
    setTimeout(() => {
      window.location.href = '/dashboard'
    }, 500)
    
  } catch (error: any) {
    console.error('Login failed:', error)
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  padding: 40px 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
