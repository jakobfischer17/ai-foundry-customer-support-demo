# AI Foundry Customer Support Demo

[![Azure AI](https://img.shields.io/badge/Azure%20AI-Foundry-0078D4?logo=microsoft-azure)](https://azure.microsoft.com/products/ai-foundry)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)

A production-ready multi-agent customer support demo powered by **Azure AI Foundry**. This application demonstrates intelligent orchestration of specialized AI agents for handling customer inquiries about products, orders, and general support.

![Demo Screenshot](docs/images/demo-screenshot.png)

## Features

- **Multi-Agent Architecture**: Three specialized agents collaborate to handle different types of customer inquiries
  - **Triage Agent**: Routes requests to the appropriate specialist
  - **Product Expert**: Answers questions about products using RAG with Azure AI Search
  - **Order Support**: Handles order status, returns, and tracking queries

- **Real-time Streaming**: Watch agent responses stream in real-time with visible agent handoffs

- **Agent Transparency**: Expandable panel shows which agents are active and what tools they're using

- **Modern Stack**: React + TypeScript frontend with FastAPI + Python backend

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Static Web Apps                     │
│                         (React Frontend)                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Azure Container Apps                         │
│                       (FastAPI Backend)                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Azure AI Foundry Agent Service              │    │
│  │  ┌──────────────┬──────────────────┬─────────────────┐  │    │
│  │  │ Triage Agent │ Product Expert   │ Order Support   │  │    │
│  │  └──────────────┴──────────────────┴─────────────────┘  │    │
│  └──────────────────────┬────────────────────┬─────────────┘    │
└─────────────────────────┼────────────────────┼──────────────────┘
                          │                    │
           ┌──────────────┘                    └──────────────┐
           ▼                                                  ▼
┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   Azure AI Search   │  │  Azure OpenAI   │  │  Azure Cosmos DB    │
│  (Product Catalog)  │  │    (GPT-4o)     │  │  (Orders & State)   │
└─────────────────────┘  └─────────────────┘  └─────────────────────┘
```

## Quick Start

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.11+](https://python.org)
- [Node.js 20+](https://nodejs.org)
- Azure subscription with access to Azure AI Foundry

### Deploy to Azure

```bash
# Clone the repository
git clone https://github.com/jakobfischer17/ai-foundry-customer-support-demo.git
cd ai-foundry-customer-support-demo

# Login to Azure
azd auth login

# Deploy everything
azd up
```

### Local Development

1. **Start the backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open http://localhost:5173

## Project Structure

```
ai-foundry-customer-support-demo/
├── frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/     # Chat UI components
│   │   ├── App.tsx         # Main application
│   │   └── types.ts        # TypeScript definitions
│   └── package.json
├── backend/                # FastAPI + Python
│   ├── agents/             # Agent definitions
│   │   ├── triage_agent.py
│   │   ├── product_agent.py
│   │   └── order_agent.py
│   ├── tools/              # Agent tools
│   │   ├── product_search.py
│   │   └── order_lookup.py
│   ├── main.py             # FastAPI application
│   └── requirements.txt
├── infra/                  # Bicep infrastructure
│   ├── main.bicep          # Main deployment
│   └── modules/            # Resource modules
├── data/                   # Seed data
│   ├── products.json       # Product catalog
│   └── orders.json         # Sample orders
└── azure.yaml              # Azure Developer CLI config
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_AI_PROJECT_CONNECTION_STRING` | AI Foundry project connection |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint |
| `AZURE_COSMOS_ENDPOINT` | Cosmos DB endpoint |

### GitHub Actions Setup

To enable CI/CD, configure these secrets in your GitHub repository:

| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `SWA_DEPLOYMENT_TOKEN` | Static Web Apps deployment token |

And these variables:

| Variable | Description |
|----------|-------------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `AZURE_RESOURCE_GROUP` | Target resource group |
| `AZURE_CONTAINER_REGISTRY` | ACR name for backend images |

## Sample Conversations

Try these prompts to see the agents in action:

- 🧴 **Product Query**: "What shampoo do you recommend for dry hair?"
- 📦 **Order Status**: "Can you check the status of my order ORD-001?"
- ↩️ **Return Request**: "I need to return a product I purchased last week"
- ❓ **General**: "What are your most popular products?"

## Technologies

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Python 3.11, FastAPI, azure-ai-projects SDK
- **AI**: Azure AI Foundry, Azure OpenAI (GPT-4o), Azure AI Search
- **Data**: Azure Cosmos DB, Azure AI Search indexes
- **Hosting**: Azure Static Web Apps, Azure Container Apps
- **IaC**: Bicep

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ using Azure AI Foundry
