import { useState } from 'react'
import { User, Bot, ChevronDown, ChevronUp, Wrench } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { Message } from '../types'

interface ChatMessageProps {
  message: Message
}

const agentColors: Record<string, string> = {
  triage_agent: 'bg-agent-triage',
  product_expert: 'bg-agent-product',
  order_support: 'bg-agent-order',
  unknown: 'bg-gray-500',
}

const agentNames: Record<string, string> = {
  triage_agent: 'Triage Agent',
  product_expert: 'Product Expert',
  order_support: 'Order Support',
  unknown: 'Agent',
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [showThoughts, setShowThoughts] = useState(false)
  const isUser = message.role === 'user'
  const hasAgentEvents = message.agentEvents && message.agentEvents.length > 0

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser
            ? 'bg-primary-600'
            : message.isError
            ? 'bg-red-500'
            : 'bg-gradient-to-br from-primary-500 to-primary-700'
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 ${
            isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'
          } ${message.isError ? 'border-red-200 bg-red-50' : ''}`}
        >
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {hasAgentEvents && (
          <div className="mt-2">
            <button
              onClick={() => setShowThoughts(!showThoughts)}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              {showThoughts ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
              <span>View agent activity ({message.agentEvents?.length} events)</span>
            </button>

            {showThoughts && (
              <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-100 text-xs space-y-2">
                {message.agentEvents?.map((event, index) => (
                  <div key={index} className="flex items-start gap-2">
                    {event.type === 'start' && (
                      <>
                        <div
                          className={`w-5 h-5 rounded-full ${agentColors[event.agent] || agentColors.unknown} flex items-center justify-center flex-shrink-0`}
                        >
                          <Bot className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-gray-600">
                          <span className="font-medium">
                            {agentNames[event.agent] || event.agent}
                          </span>{' '}
                          started processing
                        </span>
                      </>
                    )}
                    {event.type === 'tool' && (
                      <>
                        <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                          <Wrench className="w-3 h-3 text-white" />
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">
                            {event.tool}
                          </span>
                          {event.input && (
                            <pre className="mt-1 p-2 bg-gray-100 rounded text-gray-600 overflow-x-auto">
                              {JSON.stringify(event.input, null, 2)}
                            </pre>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <p className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : ''}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  )
}
