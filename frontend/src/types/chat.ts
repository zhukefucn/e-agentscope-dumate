export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface Conversation {
  id: string
  agent_id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
}

export interface SendMessageRequest {
  agent_id: string
  conversation_id?: string
  message: string
  stream?: boolean
}

export interface ChatResponse {
  conversation_id: string
  message: Message
}

export interface StreamChunk {
  type: 'content' | 'done' | 'error'
  content?: string
  message_id?: string
  conversation_id?: string
  error?: string
}
