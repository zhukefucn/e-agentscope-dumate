import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Agent, CreateAgentRequest } from '@/types/agent'
import { agentApi } from '@/services/agent'
import { ElMessage } from 'element-plus'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const availableTools = ref<string[]>([])
  const availableModels = ref<string[]>([])
  const loading = ref(false)
  const total = ref(0)

  // 获取 Agent 列表
  async function fetchAgents(page = 1, pageSize = 10) {
    try {
      loading.value = true
      const response = await agentApi.getAgents({ page, page_size: pageSize })
      agents.value = response.agents
      total.value = response.total
    } catch (error) {
      console.error('获取 Agent 列表失败:', error)
      ElMessage.error('获取 Agent 列表失败')
    } finally {
      loading.value = false
    }
  }

  // 获取单个 Agent
  async function fetchAgent(id: string) {
    try {
      loading.value = true
      currentAgent.value = await agentApi.getAgent(id)
    } catch (error) {
      console.error('获取 Agent 详情失败:', error)
      ElMessage.error('获取 Agent 详情失败')
    } finally {
      loading.value = false
    }
  }

  // 创建 Agent
  async function createAgent(data: CreateAgentRequest) {
    try {
      loading.value = true
      const agent = await agentApi.createAgent(data)
      agents.value.unshift(agent)
      ElMessage.success('创建 Agent 成功')
      return agent
    } catch (error) {
      console.error('创建 Agent 失败:', error)
      ElMessage.error('创建 Agent 失败')
      return null
    } finally {
      loading.value = false
    }
  }

  // 更新 Agent
  async function updateAgent(id: string, data: Partial<CreateAgentRequest>) {
    try {
      loading.value = true
      const agent = await agentApi.updateAgent(id, data)
      const index = agents.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        agents.value[index] = agent
      }
      if (currentAgent.value?.id === id) {
        currentAgent.value = agent
      }
      ElMessage.success('更新 Agent 成功')
      return agent
    } catch (error) {
      console.error('更新 Agent 失败:', error)
      ElMessage.error('更新 Agent 失败')
      return null
    } finally {
      loading.value = false
    }
  }

  // 删除 Agent
  async function deleteAgent(id: string) {
    try {
      loading.value = true
      await agentApi.deleteAgent(id)
      agents.value = agents.value.filter((a) => a.id !== id)
      if (currentAgent.value?.id === id) {
        currentAgent.value = null
      }
      ElMessage.success('删除 Agent 成功')
      return true
    } catch (error) {
      console.error('删除 Agent 失败:', error)
      ElMessage.error('删除 Agent 失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取可用工具
  async function fetchAvailableTools() {
    try {
      availableTools.value = await agentApi.getAvailableTools()
    } catch (error) {
      console.error('获取工具列表失败:', error)
    }
  }

  // 获取可用模型
  async function fetchAvailableModels() {
    try {
      availableModels.value = await agentApi.getAvailableModels()
    } catch (error) {
      console.error('获取模型列表失败:', error)
    }
  }

  return {
    agents,
    currentAgent,
    availableTools,
    availableModels,
    loading,
    total,
    fetchAgents,
    fetchAgent,
    createAgent,
    updateAgent,
    deleteAgent,
    fetchAvailableTools,
    fetchAvailableModels,
  }
})
