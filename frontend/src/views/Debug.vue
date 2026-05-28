<template>
  <div class="debug-container">
    <h1>调试页面</h1>
    
    <el-card class="debug-card">
      <template #header>
        <span>LocalStorage 状态</span>
      </template>
      <div>
        <p><strong>Token:</strong> {{ token ? '存在 (' + token.substring(0, 30) + '...)' : '不存在' }}</p>
        <p><strong>User:</strong> {{ userStr || '不存在' }}</p>
      </div>
    </el-card>
    
    <el-card class="debug-card">
      <template #header>
        <span>测试 API</span>
      </template>
      <div>
        <el-button @click="testLogin" type="primary">测试登录</el-button>
        <el-button @click="testGetUser" type="success">测试获取用户信息</el-button>
        <el-button @click="clearStorage" type="danger">清除 Storage</el-button>
      </div>
      <div style="margin-top: 20px;">
        <pre>{{ result }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const token = ref<string | null>(null)
const userStr = ref<string | null>(null)
const result = ref<string>('')

onMounted(() => {
  updateStorageInfo()
})

function updateStorageInfo() {
  token.value = localStorage.getItem('token')
  userStr.value = localStorage.getItem('user')
}

async function testLogin() {
  try {
    result.value = '正在登录...'
    const response = await axios.post('http://localhost:8000/api/auth/login', {
      username: 'demo',
      password: 'demo123456'
    })
    
    result.value = '登录响应:\n' + JSON.stringify(response.data, null, 2)
    
    // 保存 token
    localStorage.setItem('token', response.data.access_token)
    updateStorageInfo()
    
    result.value += '\n\nToken 已保存到 localStorage'
  } catch (error: any) {
    result.value = '登录失败:\n' + JSON.stringify(error.response?.data || error.message, null, 2)
  }
}

async function testGetUser() {
  try {
    const savedToken = localStorage.getItem('token')
    if (!savedToken) {
      result.value = '请先登录'
      return
    }
    
    result.value = '正在获取用户信息...'
    const response = await axios.get('http://localhost:8000/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${savedToken}`
      }
    })
    
    result.value = '用户信息:\n' + JSON.stringify(response.data, null, 2)
    
    // 保存用户信息
    localStorage.setItem('user', JSON.stringify(response.data))
    updateStorageInfo()
    
    result.value += '\n\n用户信息已保存到 localStorage'
  } catch (error: any) {
    result.value = '获取用户信息失败:\n' + JSON.stringify(error.response?.data || error.message, null, 2)
  }
}

function clearStorage() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  updateStorageInfo()
  result.value = 'Storage 已清除'
}
</script>

<style scoped>
.debug-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.debug-card {
  margin-bottom: 20px;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
