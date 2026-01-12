export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  agentEvents?: AgentEvent[]
  isError?: boolean
}

export interface AgentEvent {
  type: 'start' | 'tool' | 'end'
  agent: string
  tool?: string
  input?: Record<string, unknown>
  output?: unknown
  timestamp: Date
}

export interface ConversationContext {
  conversationId: string
  userId?: string
  metadata?: Record<string, unknown>
}
