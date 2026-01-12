import { Bot, Loader2 } from 'lucide-react'

interface AgentStatusProps {
  agent: string
}

const agentConfig: Record<string, { name: string; color: string; description: string }> = {
  triage_agent: {
    name: 'Triage Agent',
    color: 'bg-agent-triage',
    description: 'Analyzing your request...',
  },
  product_expert: {
    name: 'Product Expert',
    color: 'bg-agent-product',
    description: 'Searching product information...',
  },
  order_support: {
    name: 'Order Support',
    color: 'bg-agent-order',
    description: 'Looking up order details...',
  },
}

export function AgentStatus({ agent }: AgentStatusProps) {
  const config = agentConfig[agent] || {
    name: agent,
    color: 'bg-gray-500',
    description: 'Processing...',
  }

  return (
    <div className="flex gap-3">
      <div className={`w-8 h-8 rounded-full ${config.color} flex items-center justify-center flex-shrink-0 animate-pulse-slow`}>
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="chat-bubble-assistant px-4 py-3">
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
          <div>
            <p className="text-sm font-medium text-gray-700">{config.name}</p>
            <p className="text-xs text-gray-500">{config.description}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
