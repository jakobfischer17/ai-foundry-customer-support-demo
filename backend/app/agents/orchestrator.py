"""Agent orchestrator for multi-agent customer support.

This module coordinates between specialized agents:
- Triage Agent: Classifies customer intent
- Product Expert Agent: Answers product questions using RAG
- Order Support Agent: Handles order-related inquiries
"""

import os
import json
import logging
from typing import AsyncGenerator

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    Agent,
    AgentThread,
    MessageRole,
    ToolSet,
    FunctionTool,
    CodeInterpreterTool,
)

from services.cosmos_service import CosmosService
from services.search_service import SearchService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent conversations for customer support."""
    
    def __init__(
        self,
        cosmos_service: CosmosService,
        search_service: SearchService
    ):
        self.cosmos_service = cosmos_service
        self.search_service = search_service
        self.project_client: AIProjectClient = None
        self.agents: dict[str, Agent] = {}
        self.credential = DefaultAzureCredential()
        
    async def initialize(self):
        """Initialize the AI Foundry project client and create agents."""
        project_endpoint = os.getenv("AI_FOUNDRY_PROJECT_ENDPOINT")
        
        if not project_endpoint:
            logger.warning("AI_FOUNDRY_PROJECT_ENDPOINT not set, using mock mode")
            return
        
        self.project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=self.credential
        )
        
        # Create specialized agents
        await self._create_agents()
        
    async def _create_agents(self):
        """Create the specialized customer support agents."""
        
        # Triage Agent - Classifies customer intent
        self.agents["triage"] = await self.project_client.agents.create_agent(
            model="gpt-4o",
            name="Triage Agent",
            instructions="""You are a customer support triage agent for CleanHome, a consumer goods company selling cleaning and personal care products.

Your role is to:
1. Greet customers warmly
2. Understand their inquiry type
3. Route them to the appropriate specialist

Classify inquiries into:
- PRODUCT: Questions about products, ingredients, usage, recommendations
- ORDER: Questions about orders, delivery, returns, refunds
- GENERAL: General inquiries, feedback, complaints

Respond with a JSON object: {"classification": "PRODUCT|ORDER|GENERAL", "summary": "brief summary of the request"}

Be friendly and professional. If unclear, ask clarifying questions.""",
        )
        
        # Product Expert Agent - RAG-powered product knowledge
        product_tools = ToolSet()
        product_tools.add(FunctionTool(
            name="search_products",
            description="Search the product catalog for information about CleanHome products",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for products"
                    },
                    "category": {
                        "type": "string",
                        "description": "Product category filter",
                        "enum": ["shampoo", "detergent", "soap", "cleaner", "all"]
                    }
                },
                "required": ["query"]
            }
        ))
        
        self.agents["product"] = await self.project_client.agents.create_agent(
            model="gpt-4o",
            name="Product Expert",
            instructions="""You are a Product Expert for CleanHome, specializing in cleaning and personal care products.

You have deep knowledge of:
- Shampoos and hair care products
- Laundry detergents and fabric care
- Dish soaps and kitchen cleaners
- Household cleaning products
- Personal care items

When helping customers:
1. Use the search_products tool to find accurate product information
2. Explain ingredients and their benefits
3. Provide usage instructions and tips
4. Make personalized recommendations based on customer needs
5. Compare products when asked

Always be helpful, accurate, and safety-conscious. If a product isn't suitable for someone's needs, honestly recommend alternatives.""",
            tools=product_tools,
        )
        
        # Order Support Agent - Order management with tools
        order_tools = ToolSet()
        order_tools.add(FunctionTool(
            name="lookup_order",
            description="Look up order details by order ID or customer email",
            parameters={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to look up"
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer email to find orders"
                    }
                }
            }
        ))
        order_tools.add(FunctionTool(
            name="track_delivery",
            description="Get delivery tracking information for an order",
            parameters={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to track"
                    }
                },
                "required": ["order_id"]
            }
        ))
        order_tools.add(FunctionTool(
            name="initiate_return",
            description="Start a return request for an order item",
            parameters={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID for the return"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for return"
                    }
                },
                "required": ["order_id", "reason"]
            }
        ))
        
        self.agents["order"] = await self.project_client.agents.create_agent(
            model="gpt-4o",
            name="Order Support Specialist",
            instructions="""You are an Order Support Specialist for CleanHome.

You help customers with:
- Order status and tracking
- Delivery inquiries
- Returns and refunds
- Order modifications
- Payment issues

Use your tools to:
1. lookup_order: Find order details
2. track_delivery: Get shipping status
3. initiate_return: Start return process

Be empathetic and solution-oriented. Always confirm order details before making changes.
If you can't resolve an issue, explain the escalation process.""",
            tools=order_tools,
        )
        
        logger.info("All agents created successfully")
        
    async def process_message(
        self,
        session_id: str,
        message: str
    ) -> dict:
        """Process a customer message through the appropriate agent."""
        
        # Store the user message
        await self.cosmos_service.add_message(
            session_id=session_id,
            role="user",
            content=message
        )
        
        thought_process = []
        
        # Step 1: Triage the message
        thought_process.append({
            "agent": "Triage Agent",
            "action": "Classifying customer intent..."
        })
        
        classification = await self._triage_message(session_id, message)
        thought_process.append({
            "agent": "Triage Agent",
            "action": f"Classified as: {classification['classification']}",
            "details": classification.get('summary', '')
        })
        
        # Step 2: Route to appropriate agent
        agent_type = classification.get("classification", "GENERAL").upper()
        
        if agent_type == "PRODUCT":
            active_agent = "product"
            thought_process.append({
                "agent": "Product Expert",
                "action": "Searching product knowledge base..."
            })
        elif agent_type == "ORDER":
            active_agent = "order"
            thought_process.append({
                "agent": "Order Support Specialist",
                "action": "Looking up order information..."
            })
        else:
            active_agent = "triage"
            thought_process.append({
                "agent": "Triage Agent",
                "action": "Handling general inquiry..."
            })
        
        # Step 3: Get response from the selected agent
        response = await self._get_agent_response(
            session_id=session_id,
            message=message,
            agent_type=active_agent,
            classification=classification
        )
        
        thought_process.append({
            "agent": self._get_agent_display_name(active_agent),
            "action": "Generated response"
        })
        
        # Store the assistant response
        await self.cosmos_service.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
            agent=active_agent
        )
        
        return {
            "response": response,
            "agent": self._get_agent_display_name(active_agent),
            "thought_process": thought_process
        }
    
    async def process_message_stream(
        self,
        session_id: str,
        message: str
    ) -> AsyncGenerator[str, None]:
        """Stream the response for real-time updates."""
        
        # Store user message
        await self.cosmos_service.add_message(
            session_id=session_id,
            role="user",
            content=message
        )
        
        # Emit triage start
        yield json.dumps({
            "type": "thought",
            "agent": "Triage Agent",
            "content": "Analyzing your request..."
        })
        
        # Triage
        classification = await self._triage_message(session_id, message)
        agent_type = classification.get("classification", "GENERAL").upper()
        
        yield json.dumps({
            "type": "thought",
            "agent": "Triage Agent",
            "content": f"Routing to {self._get_agent_display_name(agent_type.lower())}..."
        })
        
        # Select agent
        if agent_type == "PRODUCT":
            active_agent = "product"
        elif agent_type == "ORDER":
            active_agent = "order"
        else:
            active_agent = "triage"
        
        yield json.dumps({
            "type": "agent_switch",
            "agent": self._get_agent_display_name(active_agent)
        })
        
        # Stream response
        response_text = ""
        async for chunk in self._stream_agent_response(
            session_id=session_id,
            message=message,
            agent_type=active_agent,
            classification=classification
        ):
            response_text += chunk
            yield json.dumps({
                "type": "content",
                "agent": self._get_agent_display_name(active_agent),
                "content": chunk
            })
        
        # Store response
        await self.cosmos_service.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            agent=active_agent
        )
        
        yield json.dumps({"type": "done"})
    
    async def _triage_message(self, session_id: str, message: str) -> dict:
        """Use triage agent to classify the message."""
        if not self.project_client:
            # Mock response for development
            if any(word in message.lower() for word in ["order", "delivery", "track", "return", "refund"]):
                return {"classification": "ORDER", "summary": "Order-related inquiry"}
            elif any(word in message.lower() for word in ["product", "ingredient", "recommend", "shampoo", "detergent", "soap"]):
                return {"classification": "PRODUCT", "summary": "Product inquiry"}
            return {"classification": "GENERAL", "summary": "General inquiry"}
        
        # Use actual agent
        thread = await self.project_client.agents.create_thread()
        await self.project_client.agents.create_message(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=message
        )
        
        run = await self.project_client.agents.create_run(
            thread_id=thread.id,
            agent_id=self.agents["triage"].id
        )
        
        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            run = await self.project_client.agents.get_run(
                thread_id=thread.id,
                run_id=run.id
            )
        
        messages = await self.project_client.agents.list_messages(thread_id=thread.id)
        response = messages.data[0].content[0].text.value
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"classification": "GENERAL", "summary": response}
    
    async def _get_agent_response(
        self,
        session_id: str,
        message: str,
        agent_type: str,
        classification: dict
    ) -> str:
        """Get response from the selected agent."""
        if not self.project_client:
            # Mock responses for development
            return self._get_mock_response(agent_type, message)
        
        agent = self.agents.get(agent_type, self.agents["triage"])
        
        # Get conversation history
        history = await self.cosmos_service.get_conversation_history(session_id)
        
        # Create thread with history
        thread = await self.project_client.agents.create_thread()
        
        for msg in history[-5:]:  # Last 5 messages for context
            await self.project_client.agents.create_message(
                thread_id=thread.id,
                role=MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT,
                content=msg["content"]
            )
        
        # Add current message
        await self.project_client.agents.create_message(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=message
        )
        
        # Run agent
        run = await self.project_client.agents.create_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Handle tool calls if needed
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                tool_outputs = await self._handle_tool_calls(
                    run.required_action.submit_tool_outputs.tool_calls
                )
                run = await self.project_client.agents.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            else:
                run = await self.project_client.agents.get_run(
                    thread_id=thread.id,
                    run_id=run.id
                )
        
        messages = await self.project_client.agents.list_messages(thread_id=thread.id)
        return messages.data[0].content[0].text.value
    
    async def _stream_agent_response(
        self,
        session_id: str,
        message: str,
        agent_type: str,
        classification: dict
    ) -> AsyncGenerator[str, None]:
        """Stream response from agent."""
        # For now, yield the full response in chunks
        # In production, use streaming API
        response = await self._get_agent_response(
            session_id, message, agent_type, classification
        )
        
        # Simulate streaming
        words = response.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
    
    async def _handle_tool_calls(self, tool_calls) -> list:
        """Handle tool calls from agents."""
        outputs = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            if function_name == "search_products":
                result = await self.search_service.search_products(
                    query=arguments.get("query", ""),
                    category=arguments.get("category")
                )
            elif function_name == "lookup_order":
                result = await self.cosmos_service.lookup_order(
                    order_id=arguments.get("order_id"),
                    email=arguments.get("email")
                )
            elif function_name == "track_delivery":
                result = await self.cosmos_service.track_delivery(
                    order_id=arguments["order_id"]
                )
            elif function_name == "initiate_return":
                result = await self.cosmos_service.initiate_return(
                    order_id=arguments["order_id"],
                    reason=arguments["reason"]
                )
            else:
                result = {"error": f"Unknown function: {function_name}"}
            
            outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        
        return outputs
    
    def _get_agent_display_name(self, agent_type: str) -> str:
        """Get display name for agent type."""
        names = {
            "triage": "Triage Agent",
            "product": "Product Expert",
            "order": "Order Support Specialist"
        }
        return names.get(agent_type, "Support Agent")
    
    def _get_mock_response(self, agent_type: str, message: str) -> str:
        """Get mock response for development without Azure."""
        if agent_type == "product":
            return """I'd be happy to help you with product information! 

Based on your question, let me tell you about our products:

**CleanHome Fresh Shampoo** - Our bestselling shampoo with natural ingredients:
- Aloe vera extract for moisture
- Tea tree oil for scalp health
- Paraben-free formula
- Great for daily use

Would you like more details about any specific product or recommendations based on your hair type?"""
        elif agent_type == "order":
            return """I can help you with your order! 

To look up your order, I'll need either:
- Your order number (starts with ORD-)
- Or the email address you used when ordering

Once I find your order, I can help you with:
✓ Tracking delivery status
✓ Estimated delivery date
✓ Return or exchange requests

What information can you provide?"""
        else:
            return """Hello! Welcome to CleanHome Customer Support! 👋

I'm here to help you with:

🛍️ **Product Questions** - Ingredients, usage, recommendations
📦 **Order Support** - Tracking, returns, delivery issues
💬 **General Inquiries** - Feedback, suggestions, anything else

How can I assist you today?"""
