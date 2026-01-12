import { useState } from 'react'
import { ChatContainer } from './components/ChatContainer'
import { Header } from './components/Header'
import { WelcomeScreen } from './components/WelcomeScreen'
import type { Message, AgentEvent } from './types'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [agentEvents, setAgentEvents] = useState<AgentEvent[]>([])

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setAgentEvents([])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          conversation_id: 'demo-session',
        }),
      })

      if (!response.ok) throw new Error('Failed to send message')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      let assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        agentEvents: [],
      }

      setMessages((prev) => [...prev, assistantMessage])

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter((line) => line.startsWith('data: '))

        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'agent_start') {
              setCurrentAgent(data.agent)
              const event: AgentEvent = {
                type: 'start',
                agent: data.agent,
                timestamp: new Date(),
              }
              setAgentEvents((prev) => [...prev, event])
            } else if (data.type === 'tool_call') {
              const event: AgentEvent = {
                type: 'tool',
                agent: currentAgent || 'unknown',
                tool: data.tool,
                input: data.input,
                timestamp: new Date(),
              }
              setAgentEvents((prev) => [...prev, event])
            } else if (data.type === 'content') {
              assistantMessage = {
                ...assistantMessage,
                content: assistantMessage.content + data.content,
              }
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessage.id ? assistantMessage : m
                )
              )
            } else if (data.type === 'agent_end') {
              setCurrentAgent(null)
            } else if (data.type === 'done') {
              assistantMessage = {
                ...assistantMessage,
                agentEvents: agentEvents,
              }
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessage.id ? assistantMessage : m
                )
              )
            }
          } catch {
            // Ignore parse errors for incomplete chunks
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setCurrentAgent(null)
    }
  }

  const handleQuickAction = (action: string) => {
    sendMessage(action)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      <main className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <WelcomeScreen onQuickAction={handleQuickAction} />
        ) : (
          <ChatContainer
            messages={messages}
            isLoading={isLoading}
            currentAgent={currentAgent}
            onSendMessage={sendMessage}
          />
        )}
      </main>
    </div>
  )
}

export default App
