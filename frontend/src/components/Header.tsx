import { Bot, Sparkles } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              AI Customer Support
            </h1>
            <p className="text-xs text-gray-500 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Powered by Azure AI Foundry
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Multi-Agent Demo</span>
          <div className="flex -space-x-1">
            <div className="w-6 h-6 rounded-full bg-agent-triage flex items-center justify-center text-white text-xs font-medium" title="Triage Agent">
              T
            </div>
            <div className="w-6 h-6 rounded-full bg-agent-product flex items-center justify-center text-white text-xs font-medium" title="Product Expert">
              P
            </div>
            <div className="w-6 h-6 rounded-full bg-agent-order flex items-center justify-center text-white text-xs font-medium" title="Order Support">
              O
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
