export interface Agent {
  id: string
  name: string
  description: string
  system_prompt: string
  model_name: string
  tools: string[]
  temperature?: number
  max_tokens?: number
  user_id: string
  created_at: string
  updated_at: string
}

export interface CreateAgentRequest {
  name: string
  description: string
  system_prompt: string
  model_name: string
  tools: string[]
  temperature?: number
  max_tokens?: number
}

export interface UpdateAgentRequest {
  name?: string
  description?: string
  system_prompt?: string
  model_name?: string
  tools?: string[]
  temperature?: number
  max_tokens?: number
}

export interface AgentListResponse {
  agents: Agent[]
  total: number
  page: number
  page_size: number
}
