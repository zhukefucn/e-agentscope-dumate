<template>
  <div class="chat-container">
    <!-- 左侧对话列表 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <el-button type="primary" @click="createNewConversation" :icon="Plus" round>
          新建对话
        </el-button>
        <el-button 
          :icon="sidebarCollapsed ? Expand : Fold" 
          @click="sidebarCollapsed = !sidebarCollapsed"
          text
          class="collapse-btn"
        />
      </div>
      
      <div class="conversation-list" v-show="!sidebarCollapsed">
        <el-scrollbar>
          <div
            v-for="conv in conversations"
            :key="conv.id"
            class="conversation-item"
            :class="{ active: currentConversation?.id === conv.id }"
            @click="selectConversation(conv)"
          >
            <el-icon><ChatDotRound /></el-icon>
            <span class="conv-title">{{ conv.title }}</span>
            <el-button
              :icon="Delete"
              text
              size="small"
              @click.stop="handleDeleteConversation(conv.id)"
              class="delete-btn"
            />
          </div>
          <el-empty v-if="conversations.length === 0" description="暂无对话" />
        </el-scrollbar>
      </div>
    </div>

    <!-- 右侧主对话区域 -->
    <div class="main-chat">
      <!-- 顶部信息栏 -->
      <div class="chat-header">
        <div class="header-left">
          <el-button 
            :icon="sidebarCollapsed ? Expand : Fold" 
            @click="sidebarCollapsed = !sidebarCollapsed"
            text
            class="toggle-sidebar-btn"
          />
          <div class="agent-info" v-if="currentAgent">
            <el-avatar :size="32" class="agent-avatar">
              {{ currentAgent.name.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="agent-details">
              <span class="agent-name">{{ currentAgent.name }}</span>
              <span class="agent-model">{{ currentAgent.model_name }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <span class="conversation-title" v-if="currentConversation">
            {{ currentConversation.title }}
          </span>
          <el-button :icon="Setting" text @click="showAgentSelect = true">
            切换 Agent
          </el-button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <el-scrollbar ref="scrollbarRef">
          <div class="messages-wrapper">
            <div v-if="messages.length === 0" class="empty-chat">
              <el-icon :size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
              <p>开始与 {{ currentAgent?.name || 'Agent' }} 对话吧</p>
            </div>
            
            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message-item"
              :class="msg.role"
            >
              <div class="message-avatar">
                <el-avatar v-if="msg.role === 'user'" :size="36">
                  {{ userStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
                </el-avatar>
                <el-avatar v-else :size="36" class="ai-avatar">
                  {{ currentAgent?.name?.charAt(0).toUpperCase() || 'A' }}
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="message-role">
                  {{ msg.role === 'user' ? '你' : currentAgent?.name || 'AI' }}
                </div>
                <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
              </div>
            </div>
            
            <!-- 正在输入提示 -->
            <div v-if="isStreaming" class="message-item assistant streaming">
              <div class="message-avatar">
                <el-avatar :size="36" class="ai-avatar">
                  {{ currentAgent?.name?.charAt(0).toUpperCase() || 'A' }}
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="message-role">{{ currentAgent?.name || 'AI' }}</div>
                <div class="message-text" v-html="renderMarkdown(streamingContent)"></div>
                <span class="typing-indicator">
                  <span></span><span></span><span></span>
                </span>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <!-- 底部输入区 -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            :autosize="{ minRows: 3, maxRows: 8 }"
            placeholder="输入消息... (Shift+Enter 换行，Enter 发送)"
            @keydown.enter.exact="handleSend"
            @keydown.enter.shift.exact.stop
            :disabled="isStreaming"
          />
          <div class="input-actions">
            <el-button
              type="primary"
              :icon="isStreaming ? Loading : Position"
              @click="handleSend"
              :disabled="!inputMessage.trim() || isStreaming"
              :loading="isStreaming"
            >
              {{ isStreaming ? '发送中' : '发送' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Agent 选择对话框 -->
    <el-dialog v-model="showAgentSelect" title="选择 Agent" width="500px">
      <el-input
        v-model="agentSearchKeyword"
        placeholder="搜索 Agent"
        :prefix-icon="Search"
        clearable
        style="margin-bottom: 16px"
      />
      <div class="agent-select-list">
        <div
          v-for="agent in filteredAgents"
          :key="agent.id"
          class="agent-select-item"
          :class="{ active: currentAgent?.id === agent.id }"
          @click="selectAgent(agent)"
        >
          <el-avatar :size="40">{{ agent.name.charAt(0).toUpperCase() }}</el-avatar>
          <div class="agent-info">
            <div class="agent-name">{{ agent.name }}</div>
            <div class="agent-desc">{{ agent.description }}</div>
          </div>
          <el-icon v-if="currentAgent?.id === agent.id" color="#409eff"><Check /></el-icon>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  ChatDotRound,
  Position,
  Setting,
  Search,
  Check,
  Fold,
  Expand,
  Loading,
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { chatApi } from '@/services/chat'
import { agentApi } from '@/services/agent'
import { useAgentStore } from '@/stores/agent'
import { useUserStore } from '@/stores/user'
import type { Conversation, Message } from '@/types/chat'
import type { Agent } from '@/types/agent'

// 配置 marked 使用 highlight.js
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

const route = useRoute()
const router = useRouter()
const agentStore = useAgentStore()
const userStore = useUserStore()

// 状态
const sidebarCollapsed = ref(false)
const conversations = ref<Conversation[]>([])
const currentConversation = ref<Conversation | null>(null)
const messages = ref<Message[]>([])
const inputMessage = ref('')
const isStreaming = ref(false)
const streamingContent = ref('')
const currentAgent = ref<Agent | null>(null)
const showAgentSelect = ref(false)
const agentSearchKeyword = ref('')
const messageListRef = ref<HTMLElement>()
const scrollbarRef = ref()

// 计算属性
const filteredAgents = computed(() => {
  if (!agentSearchKeyword.value) return agentStore.agents
  const keyword = agentSearchKeyword.value.toLowerCase()
  return agentStore.agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(keyword) ||
      agent.description.toLowerCase().includes(keyword)
  )
})

// 初始化
onMounted(async () => {
  await agentStore.fetchAgents()
  
  // 从路由参数获取 agentId
  const agentId = route.params.agentId as string
  if (agentId) {
    await loadAgent(agentId)
  } else if (agentStore.agents.length > 0) {
    currentAgent.value = agentStore.agents[0]
  }
  
  await loadConversations()
})

// 监听路由参数变化
watch(
  () => route.params.agentId,
  async (newAgentId) => {
    if (newAgentId) {
      await loadAgent(newAgentId as string)
    }
  }
)

// 加载 Agent
async function loadAgent(agentId: string) {
  try {
    currentAgent.value = await agentApi.getAgent(agentId)
  } catch (error) {
    ElMessage.error('加载 Agent 失败')
  }
}

// 加载对话列表
async function loadConversations() {
  try {
    const agentId = currentAgent.value?.id
    conversations.value = await chatApi.getConversations(agentId)
  } catch (error) {
    console.error('加载对话列表失败:', error)
  }
}

// 选择对话
async function selectConversation(conv: Conversation) {
  currentConversation.value = conv
  try {
    messages.value = await chatApi.getConversationMessages(conv.id)
    await scrollToBottom()
  } catch (error) {
    ElMessage.error('加载对话消息失败')
  }
}

// 创建新对话
function createNewConversation() {
  currentConversation.value = null
  messages.value = []
}

// 删除对话
async function handleDeleteConversation(conversationId: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    await chatApi.deleteConversation(conversationId)
    conversations.value = conversations.value.filter((c) => c.id !== conversationId)
    
    if (currentConversation.value?.id === conversationId) {
      createNewConversation()
    }
    
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 选择 Agent
async function selectAgent(agent: Agent) {
  currentAgent.value = agent
  showAgentSelect.value = false
  createNewConversation()
  await loadConversations()
}

// 发送消息
async function handleSend() {
  if (!inputMessage.value.trim() || isStreaming.value || !currentAgent.value) {
    if (!currentAgent.value) {
      ElMessage.warning('请先选择一个 Agent')
    }
    return
  }

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  isStreaming.value = true
  streamingContent.value = ''

  // 添加用户消息到列表
  const tempUserMsg: Message = {
    id: `temp-${Date.now()}`,
    conversation_id: currentConversation.value?.id || '',
    role: 'user',
    content: userMessage,
    created_at: new Date().toISOString(),
  }
  messages.value.push(tempUserMsg)
  await scrollToBottom()

  try {
    await chatApi.sendMessageStream(
      {
        agent_id: currentAgent.value.id,
        conversation_id: currentConversation.value?.id,
        message: userMessage,
        stream: true,
      },
      // onChunk
      (chunk) => {
        streamingContent.value += chunk
        scrollToBottom()
      },
      // onError
      (error) => {
        ElMessage.error(error)
        isStreaming.value = false
        streamingContent.value = ''
      },
      // onComplete
      async (messageId, conversationId) => {
        // 添加 AI 消息到列表
        const aiMessage: Message = {
          id: messageId,
          conversation_id: conversationId,
          role: 'assistant',
          content: streamingContent.value,
          created_at: new Date().toISOString(),
        }
        messages.value.push(aiMessage)
        
        // 如果是新对话，更新对话列表
        if (!currentConversation.value) {
          await loadConversations()
          const newConv = conversations.value.find((c) => c.id === conversationId)
          if (newConv) {
            currentConversation.value = newConv
          }
        }
        
        isStreaming.value = false
        streamingContent.value = ''
        await scrollToBottom()
      }
    )
  } catch (error) {
    ElMessage.error('发送消息失败')
    isStreaming.value = false
    streamingContent.value = ''
  }
}

// 渲染 Markdown
function renderMarkdown(content: string): string {
  if (!content) return ''
  return marked.parse(content) as string
}

// 滚动到底部
async function scrollToBottom() {
  await nextTick()
  if (scrollbarRef.value) {
    const scrollbar = scrollbarRef.value
    scrollbar.setScrollTop(scrollbar.wrapRef.scrollHeight)
  }
}
</script>

<style scoped lang="scss">
.chat-container {
  display: flex;
  height: calc(100vh - 60px - 40px); // 减去 header 和 main padding
  margin: -20px; // 抵消 layout-main 的 padding
  background: #f5f7fa;
}

// 左侧边栏
.sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  
  &.collapsed {
    width: 60px;
    
    .sidebar-header {
      padding: 16px 8px;
      justify-content: center;
    }
  }
}

.sidebar-header {
  padding: 16px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #e4e7ed;
  
  .el-button--primary {
    flex: 1;
  }
  
  .collapse-btn {
    display: none;
  }
}

.conversation-list {
  flex: 1;
  overflow: hidden;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #f0f0f0;
  
  &:hover {
    background: #f5f7fa;
    
    .delete-btn {
      opacity: 1;
    }
  }
  
  &.active {
    background: #ecf5ff;
    
    .conv-title {
      color: #409eff;
      font-weight: 500;
    }
  }
  
  .el-icon {
    margin-right: 10px;
    color: #909399;
  }
  
  .conv-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 14px;
  }
  
  .delete-btn {
    opacity: 0;
    transition: opacity 0.2s;
  }
}

// 主对话区域
.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .toggle-sidebar-btn {
    display: none;
  }
  
  .agent-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .agent-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
  }
  
  .agent-details {
    display: flex;
    flex-direction: column;
    
    .agent-name {
      font-weight: 500;
      font-size: 15px;
    }
    
    .agent-model {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .conversation-title {
    font-size: 14px;
    color: #606266;
  }
}

// 消息列表
.message-list {
  flex: 1;
  overflow: hidden;
  background: #f5f7fa;
  
  .messages-wrapper {
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
  }
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
  
  p {
    margin-top: 16px;
    font-size: 16px;
  }
}

.message-item {
  display: flex;
  margin-bottom: 24px;
  
  &.user {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-text {
      background: #409eff;
      color: #fff;
      border-radius: 16px 16px 4px 16px;
    }
  }
  
  &.assistant {
    .message-text {
      background: #fff;
      border-radius: 16px 16px 16px 4px;
    }
  }
  
  &.streaming {
    .message-text {
      min-height: 40px;
    }
  }
}

.message-avatar {
  flex-shrink: 0;
  margin: 0 12px;
  
  .ai-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-role {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.message-text {
  padding: 12px 16px;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  :deep(pre) {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin: 8px 0;
    
    code {
      color: #d4d4d4;
      font-size: 13px;
    }
  }
  
  :deep(code:not(pre code)) {
    background: rgba(0, 0, 0, 0.06);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
  }
  
  :deep(p) {
    margin: 0 0 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  :deep(ul), :deep(ol) {
    padding-left: 20px;
    margin: 8px 0;
  }
  
  :deep(table) {
    border-collapse: collapse;
    margin: 8px 0;
    width: 100%;
    
    th, td {
      border: 1px solid #e4e7ed;
      padding: 8px 12px;
      text-align: left;
    }
    
    th {
      background: #f5f7fa;
    }
  }
}

// 打字指示器
.typing-indicator {
  display: inline-flex;
  gap: 4px;
  margin-left: 8px;
  
  span {
    width: 6px;
    height: 6px;
    background: #409eff;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: 0s; }
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

// 输入区域
.input-area {
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  
  .input-wrapper {
    max-width: 900px;
    margin: 0 auto;
    
    :deep(.el-textarea__inner) {
      border-radius: 12px;
      padding: 12px 16px;
      font-size: 15px;
      line-height: 1.6;
      resize: none;
      
      &:focus {
        box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
      }
    }
  }
  
  .input-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
}

// Agent 选择对话框
.agent-select-list {
  max-height: 400px;
  overflow-y: auto;
}

.agent-select-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  
  &:hover {
    background: #f5f7fa;
  }
  
  &.active {
    background: #ecf5ff;
  }
  
  .el-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    flex-shrink: 0;
  }
  
  .agent-info {
    flex: 1;
    margin-left: 12px;
    overflow: hidden;
    
    .agent-name {
      font-weight: 500;
      font-size: 15px;
    }
    
    .agent-desc {
      font-size: 13px;
      color: #909399;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    
    &.collapsed {
      width: 0;
      overflow: hidden;
    }
    
    .sidebar-header .collapse-btn {
      display: flex;
    }
  }
  
  .chat-header .toggle-sidebar-btn {
    display: flex;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>
