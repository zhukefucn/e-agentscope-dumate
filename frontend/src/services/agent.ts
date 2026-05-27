import { api } from './api'
import type { Agent, CreateAgentRequest, UpdateAgentRequest, AgentListResponse } from '@/types/agent'

export const agentApi = {
  // 获取 Agent 列表
  getAgents(params?: { page?: number; page_size?: number }): Promise<AgentListResponse> {
    return api.get<AgentListResponse>('/agents', { params })
  },

  // 获取单个 Agent
  getAgent(id: string): Promise<Agent> {
    return api.get<Agent>(`/agents/${id}`)
  },

  // 创建 Agent
  createAgent(data: CreateAgentRequest): Promise<Agent> {
    return api.post<Agent>('/agents', data)
  },

  // 更新 Agent
  updateAgent(id: string, data: UpdateAgentRequest): Promise<Agent> {
    return api.put<Agent>(`/agents/${id}`, data)
  },

  // 删除 Agent
  deleteAgent(id: string): Promise<void> {
    return api.delete(`/agents/${id}`)
  },

  // 获取可用工具列表
  getAvailableTools(): Promise<string[]> {
    return api.get<string[]>('/agents/tools')
  },

  // 获取可用模型列表
  getAvailableModels(): Promise<string[]> {
    return api.get<string[]>('/agents/models')
  },
}
