import { Package, ShoppingCart, HelpCircle, MessageSquare } from 'lucide-react'

interface WelcomeScreenProps {
  onQuickAction: (action: string) => void
}

const quickActions = [
  {
    icon: Package,
    label: 'Product Info',
    prompt: 'What shampoo do you recommend for dry hair?',
    color: 'bg-agent-product',
  },
  {
    icon: ShoppingCart,
    label: 'Order Status',
    prompt: 'Can you check the status of my order ORD-001?',
    color: 'bg-agent-order',
  },
  {
    icon: HelpCircle,
    label: 'Return Help',
    prompt: 'I need to return a product I purchased last week',
    color: 'bg-agent-triage',
  },
  {
    icon: MessageSquare,
    label: 'General Question',
    prompt: 'What are your most popular products?',
    color: 'bg-primary-500',
  },
]

export function WelcomeScreen({ onQuickAction }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      <div className="max-w-2xl text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <MessageSquare className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to AI Customer Support
        </h2>
        <p className="text-gray-600 mb-8">
          I'm here to help with product questions, order status, returns, and more.
          Our intelligent agents work together to provide you the best assistance.
        </p>

        <div className="grid grid-cols-2 gap-3 mb-8">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => onQuickAction(action.prompt)}
              className="flex items-center gap-3 p-4 bg-white rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all text-left group"
            >
              <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform`}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-medium text-gray-900">{action.label}</p>
                <p className="text-xs text-gray-500 line-clamp-1">
                  {action.prompt}
                </p>
              </div>
            </button>
          ))}
        </div>

        <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-agent-triage" />
            <span>Triage Agent</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-agent-product" />
            <span>Product Expert</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-agent-order" />
            <span>Order Support</span>
          </div>
        </div>
      </div>
    </div>
  )
}
