import type { SendMessageRequest, ChatResponse, Conversation, Message } from '@/types/chat'

const API_BASE = '/api'

export const chatApi = {
  // 发送消息（非流式）
  sendMessage(data: SendMessageRequest): Promise<ChatResponse> {
    return fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ ...data, stream: false }),
    }).then((res) => {
      if (!res.ok) {
        throw new Error('请求失败')
      }
      return res.json()
    })
  },

  // 发送消息（流式）
  async sendMessageStream(
    data: SendMessageRequest,
    onChunk: (chunk: string) => void,
    onError?: (error: string) => void,
    onComplete?: (messageId: string, conversationId: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ ...data, stream: true }),
      })

      if (!response.ok) {
        throw new Error('请求失败')
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法读取响应流')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              continue
            }

            try {
              const parsed = JSON.parse(data)
              
              if (parsed.type === 'content') {
                onChunk(parsed.content || '')
              } else if (parsed.type === 'done') {
                onComplete?.(parsed.message_id, parsed.conversation_id)
              } else if (parsed.type === 'error') {
                onError?.(parsed.error || '未知错误')
              }
            } catch (e) {
              console.error('解析 SSE 数据失败:', e)
            }
          }
        }
      }
    } catch (error) {
      onError?.(error instanceof Error ? error.message : '未知错误')
    }
  },

  // 获取对话列表
  getConversations(agentId?: string): Promise<Conversation[]> {
    const params = agentId ? { agent_id: agentId } : {}
    return fetch(`${API_BASE}/chat/conversations`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }).then((res) => res.json())
  },

  // 获取对话历史
  getConversationMessages(conversationId: string): Promise<Message[]> {
    return fetch(`${API_BASE}/chat/conversations/${conversationId}/messages`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }).then((res) => res.json())
  },

  // 删除对话
  deleteConversation(conversationId: string): Promise<void> {
    return fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }).then((res) => {
      if (!res.ok) throw new Error('删除失败')
    })
  },
}
