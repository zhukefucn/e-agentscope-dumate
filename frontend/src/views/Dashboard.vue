<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1>欢迎回来，{{ userStore.user?.username || '用户' }}</h1>
        <p>开始与您的智能 Agent 对话，探索 AI 的无限可能</p>
      </div>
      <div class="welcome-illustration">
        <el-icon :size="120" color="#409eff"><Monitor /></el-icon>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <h2>快捷操作</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <div class="action-card create-agent" @click="goToCreateAgent">
            <div class="action-icon">
              <el-icon :size="40"><Plus /></el-icon>
            </div>
            <div class="action-info">
              <h3>创建 Agent</h3>
              <p>创建一个新的智能助手</p>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <div class="action-card start-chat" @click="goToChat">
            <div class="action-icon">
              <el-icon :size="40"><ChatDotRound /></el-icon>
            </div>
            <div class="action-info">
              <h3>开始对话</h3>
              <p>与 Agent 开始新对话</p>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <div class="action-card manage-agents" @click="goToAgentList">
            <div class="action-icon">
              <el-icon :size="40"><List /></el-icon>
            </div>
            <div class="action-info">
              <h3>管理 Agent</h3>
              <p>查看和管理所有 Agent</p>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <div class="action-card view-docs" @click="openDocs">
            <div class="action-icon">
              <el-icon :size="40"><Document /></el-icon>
            </div>
            <div class="action-info">
              <h3>使用文档</h3>
              <p>查看使用指南和文档</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <h2>数据统计</h2>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-value">{{ stats.agentCount }}</div>
            <div class="stat-label">Agent 数量</div>
            <el-icon class="stat-icon"><User /></el-icon>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-value">{{ stats.conversationCount }}</div>
            <div class="stat-label">对话数量</div>
            <el-icon class="stat-icon"><ChatDotRound /></el-icon>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-value">{{ stats.messageCount }}</div>
            <div class="stat-label">消息数量</div>
            <el-icon class="stat-icon"><Message /></el-icon>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-value">{{ stats.todayMessages }}</div>
            <div class="stat-label">今日消息</div>
            <el-icon class="stat-icon"><TrendCharts /></el-icon>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 最近使用的 Agent -->
    <div class="recent-agents">
      <div class="section-header">
        <h2>最近使用的 Agent</h2>
        <el-button text @click="goToAgentList">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      
      <div v-if="recentAgents.length > 0" class="agent-grid">
        <el-row :gutter="20">
          <el-col 
            v-for="agent in recentAgents" 
            :key="agent.id" 
            :xs="24" 
            :sm="12" 
            :md="8" 
            :lg="6"
          >
            <div class="agent-card" @click="startChatWithAgent(agent)">
              <div class="agent-header">
                <el-avatar :size="48" class="agent-avatar">
                  {{ agent.name.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="agent-title">
                  <h3>{{ agent.name }}</h3>
                  <span class="agent-model">{{ agent.model_name }}</span>
                </div>
              </div>
              <p class="agent-description">{{ agent.description || '暂无描述' }}</p>
              <div class="agent-tools" v-if="agent.tools && agent.tools.length > 0">
                <el-tag 
                  v-for="tool in agent.tools.slice(0, 3)" 
                  :key="tool" 
                  size="small" 
                  type="info"
                >
                  {{ tool }}
                </el-tag>
                <el-tag v-if="agent.tools.length > 3" size="small" type="info">
                  +{{ agent.tools.length - 3 }}
                </el-tag>
              </div>
              <div class="agent-actions">
                <el-button type="primary" size="small" :icon="ChatDotRound">
                  开始对话
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <el-empty v-else description="暂无 Agent，快去创建一个吧">
        <el-button type="primary" @click="goToCreateAgent">创建 Agent</el-button>
      </el-empty>
    </div>

    <!-- 快速开始对话 -->
    <div class="quick-start" v-if="recentAgents.length > 0">
      <h2>快速开始</h2>
      <div class="quick-chat">
        <el-select
          v-model="selectedAgentId"
          placeholder="选择一个 Agent"
          style="width: 300px"
        >
          <el-option
            v-for="agent in agentStore.agents"
            :key="agent.id"
            :label="agent.name"
            :value="agent.id"
          >
            <div class="agent-option">
              <el-avatar :size="24" class="agent-avatar-small">
                {{ agent.name.charAt(0).toUpperCase() }}
              </el-avatar>
              <span>{{ agent.name }}</span>
              <span class="agent-model-small">{{ agent.model_name }}</span>
            </div>
          </el-option>
        </el-select>
        <el-input
          v-model="quickMessage"
          placeholder="输入消息快速开始对话..."
          @keyup.enter="quickStartChat"
          style="flex: 1; margin: 0 16px"
        >
          <template #prefix>
            <el-icon><Edit /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" :icon="Position" @click="quickStartChat">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  ChatDotRound,
  List,
  Document,
  User,
  Message,
  TrendCharts,
  ArrowRight,
  Position,
  Edit,
  Monitor,
} from '@element-plus/icons-vue'
import { useAgentStore } from '@/stores/agent'
import { useUserStore } from '@/stores/user'
import { chatApi } from '@/services/chat'
import type { Agent } from '@/types/agent'

const router = useRouter()
const agentStore = useAgentStore()
const userStore = useUserStore()

// 状态
const stats = ref({
  agentCount: 0,
  conversationCount: 0,
  messageCount: 0,
  todayMessages: 0,
})
const selectedAgentId = ref('')
const quickMessage = ref('')

// 计算属性
const recentAgents = computed(() => {
  return agentStore.agents.slice(0, 4)
})

// 初始化
onMounted(async () => {
  await Promise.all([
    agentStore.fetchAgents(1, 100),
    loadStats(),
  ])
  
  if (agentStore.agents.length > 0) {
    selectedAgentId.value = agentStore.agents[0].id
  }
})

// 加载统计数据
async function loadStats() {
  try {
    // 获取 Agent 数量
    stats.value.agentCount = agentStore.total
    
    // 获取对话数量
    const conversations = await chatApi.getConversations()
    stats.value.conversationCount = conversations.length
    
    // 模拟其他统计数据（实际应从后端获取）
    stats.value.messageCount = conversations.length * 10
    stats.value.todayMessages = Math.floor(Math.random() * 20)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 导航方法
function goToCreateAgent() {
  router.push('/agents/create')
}

function goToAgentList() {
  router.push('/agents')
}

function goToChat() {
  if (agentStore.agents.length > 0) {
    router.push(`/chat/${agentStore.agents[0].id}`)
  } else {
    ElMessage.warning('请先创建一个 Agent')
    router.push('/agents/create')
  }
}

function startChatWithAgent(agent: Agent) {
  router.push(`/chat/${agent.id}`)
}

function quickStartChat() {
  if (!selectedAgentId.value) {
    ElMessage.warning('请选择一个 Agent')
    return
  }
  if (!quickMessage.value.trim()) {
    ElMessage.warning('请输入消息')
    return
  }
  
  // 存储快速消息到 sessionStorage，在 Chat 页面读取并发送
  sessionStorage.setItem('quickMessage', quickMessage.value)
  router.push(`/chat/${selectedAgentId.value}`)
}

function openDocs() {
  ElMessage.info('文档功能开发中')
}
</script>

<style scoped lang="scss">
.dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

// 欢迎区域
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 32px;
  color: #fff;
  
  .welcome-content {
    h1 {
      font-size: 28px;
      font-weight: 600;
      margin-bottom: 12px;
    }
    
    p {
      font-size: 16px;
      opacity: 0.9;
    }
  }
  
  .welcome-illustration {
    opacity: 0.3;
  }
}

// 快捷操作
.quick-actions {
  margin-bottom: 32px;
  
  h2 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #303133;
  }
}

.action-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
  margin-bottom: 20px;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .action-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    color: #fff;
  }
  
  &.create-agent .action-icon {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  &.start-chat .action-icon {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  }
  
  &.manage-agents .action-icon {
    background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  }
  
  &.view-docs .action-icon {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }
  
  .action-info {
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 4px;
      color: #303133;
    }
    
    p {
      font-size: 13px;
      color: #909399;
    }
  }
}

// 统计信息
.stats-section {
  margin-bottom: 32px;
  
  h2 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #303133;
  }
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  border: 1px solid #e4e7ed;
  margin-bottom: 20px;
  
  .stat-value {
    font-size: 36px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 8px;
  }
  
  .stat-label {
    font-size: 14px;
    color: #909399;
  }
  
  .stat-icon {
    position: absolute;
    right: 20px;
    bottom: 20px;
    font-size: 48px;
    color: #e4e7ed;
  }
}

// 最近使用的 Agent
.recent-agents {
  margin-bottom: 32px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h2 {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.agent-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
  margin-bottom: 20px;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .agent-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }
  
  .agent-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    margin-right: 12px;
  }
  
  .agent-title {
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 2px;
      color: #303133;
    }
    
    .agent-model {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .agent-description {
    font-size: 13px;
    color: #606266;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.5;
  }
  
  .agent-tools {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
  }
  
  .agent-actions {
    display: flex;
    justify-content: flex-end;
  }
}

// 快速开始
.quick-start {
  h2 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #303133;
  }
  
  .quick-chat {
    display: flex;
    align-items: center;
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #e4e7ed;
  }
}

.agent-option {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .agent-avatar-small {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
  }
  
  .agent-model-small {
    font-size: 12px;
    color: #909399;
    margin-left: auto;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .welcome-section {
    flex-direction: column;
    text-align: center;
    padding: 24px;
    
    .welcome-illustration {
      display: none;
    }
    
    .welcome-content {
      h1 {
        font-size: 22px;
      }
    }
  }
  
  .quick-chat {
    flex-direction: column;
    gap: 12px;
    
    .el-select {
      width: 100% !important;
    }
    
    .el-input {
      margin: 0 !important;
    }
  }
}
</style>
