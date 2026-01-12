"""Cosmos DB service for order management and conversation history."""

import os
import logging
from datetime import datetime
from typing import Optional

from azure.identity.aio import DefaultAzureCredential
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

logger = logging.getLogger(__name__)


class CosmosService:
    """Service for managing orders and conversations in Cosmos DB."""
    
    def __init__(self):
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.database_name = "customer-support"
        self.orders_container = "orders"
        self.conversations_container = "conversations"
        self.client: CosmosClient = None
        self.database = None
        self._initialized = False
        
        # Mock data for development
        self._mock_orders = {
            "ORD-001": {
                "id": "ORD-001",
                "customerId": "cust-123",
                "email": "john@example.com",
                "status": "shipped",
                "items": [
                    {"name": "Fresh Clean Shampoo", "quantity": 2, "price": 12.99},
                    {"name": "Ocean Breeze Detergent", "quantity": 1, "price": 18.99}
                ],
                "total": 44.97,
                "orderDate": "2026-01-08",
                "estimatedDelivery": "2026-01-14",
                "trackingNumber": "1Z999AA10123456784",
                "carrier": "UPS"
            },
            "ORD-002": {
                "id": "ORD-002",
                "customerId": "cust-456",
                "email": "jane@example.com",
                "status": "delivered",
                "items": [
                    {"name": "Gentle Hand Soap", "quantity": 3, "price": 5.99}
                ],
                "total": 17.97,
                "orderDate": "2026-01-05",
                "deliveredDate": "2026-01-10"
            }
        }
        self._mock_conversations = {}
    
    async def _ensure_initialized(self):
        """Initialize Cosmos client if not already done."""
        if self._initialized:
            return
            
        if not self.endpoint:
            logger.warning("COSMOS_ENDPOINT not set, using mock data")
            self._initialized = True
            return
        
        try:
            credential = DefaultAzureCredential()
            self.client = CosmosClient(self.endpoint, credential=credential)
            self.database = self.client.get_database_client(self.database_name)
            self._initialized = True
            logger.info("Cosmos DB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            self._initialized = True  # Use mock data
    
    async def create_session(self, session_id: str) -> dict:
        """Create a new conversation session."""
        await self._ensure_initialized()
        
        session = {
            "id": session_id,
            "sessionId": session_id,
            "messages": [],
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
        
        if self.client:
            container = self.database.get_container_client(self.conversations_container)
            await container.create_item(body=session)
        else:
            self._mock_conversations[session_id] = session
        
        return session
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent: Optional[str] = None
    ):
        """Add a message to a conversation session."""
        await self._ensure_initialized()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        if agent:
            message["agent"] = agent
        
        if self.client:
            container = self.database.get_container_client(self.conversations_container)
            session = await container.read_item(
                item=session_id,
                partition_key=session_id
            )
            session["messages"].append(message)
            session["updatedAt"] = datetime.utcnow().isoformat()
            await container.replace_item(item=session_id, body=session)
        else:
            if session_id not in self._mock_conversations:
                await self.create_session(session_id)
            self._mock_conversations[session_id]["messages"].append(message)
    
    async def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session."""
        await self._ensure_initialized()
        
        if self.client:
            container = self.database.get_container_client(self.conversations_container)
            try:
                session = await container.read_item(
                    item=session_id,
                    partition_key=session_id
                )
                return session.get("messages", [])
            except:
                return []
        else:
            session = self._mock_conversations.get(session_id, {})
            return session.get("messages", [])
    
    async def get_order(self, order_id: str) -> Optional[dict]:
        """Get order by ID."""
        await self._ensure_initialized()
        
        if self.client:
            container = self.database.get_container_client(self.orders_container)
            try:
                query = f"SELECT * FROM c WHERE c.id = @orderId"
                items = container.query_items(
                    query=query,
                    parameters=[{"name": "@orderId", "value": order_id}]
                )
                async for item in items:
                    return item
                return None
            except:
                return None
        else:
            return self._mock_orders.get(order_id)
    
    async def lookup_order(
        self,
        order_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> dict:
        """Look up order by ID or email."""
        await self._ensure_initialized()
        
        if order_id:
            order = await self.get_order(order_id)
            if order:
                return {"found": True, "order": order}
            return {"found": False, "message": f"Order {order_id} not found"}
        
        if email:
            # Search by email
            if self.client:
                container = self.database.get_container_client(self.orders_container)
                query = "SELECT * FROM c WHERE c.email = @email"
                items = container.query_items(
                    query=query,
                    parameters=[{"name": "@email", "value": email}]
                )
                orders = [item async for item in items]
                return {"found": len(orders) > 0, "orders": orders}
            else:
                orders = [
                    o for o in self._mock_orders.values()
                    if o.get("email") == email
                ]
                return {"found": len(orders) > 0, "orders": orders}
        
        return {"found": False, "message": "Please provide order ID or email"}
    
    async def track_delivery(self, order_id: str) -> dict:
        """Get delivery tracking information."""
        order = await self.get_order(order_id)
        
        if not order:
            return {"found": False, "message": f"Order {order_id} not found"}
        
        status = order.get("status", "unknown")
        
        tracking_info = {
            "orderId": order_id,
            "status": status,
            "carrier": order.get("carrier", "N/A"),
            "trackingNumber": order.get("trackingNumber", "N/A"),
        }
        
        if status == "shipped":
            tracking_info["estimatedDelivery"] = order.get("estimatedDelivery")
            tracking_info["message"] = "Your order is on its way!"
        elif status == "delivered":
            tracking_info["deliveredDate"] = order.get("deliveredDate")
            tracking_info["message"] = "Your order has been delivered."
        elif status == "processing":
            tracking_info["message"] = "Your order is being prepared for shipment."
        
        return tracking_info
    
    async def initiate_return(self, order_id: str, reason: str) -> dict:
        """Initiate a return request."""
        order = await self.get_order(order_id)
        
        if not order:
            return {"success": False, "message": f"Order {order_id} not found"}
        
        if order.get("status") != "delivered":
            return {
                "success": False,
                "message": "Returns can only be initiated for delivered orders"
            }
        
        # Create return request
        return_id = f"RET-{order_id}"
        
        return {
            "success": True,
            "returnId": return_id,
            "message": f"Return request {return_id} created successfully",
            "instructions": [
                "You will receive a prepaid shipping label via email within 24 hours",
                "Pack the items securely in original packaging if possible",
                "Drop off at any UPS location",
                "Refund will be processed within 5-7 business days after we receive the items"
            ],
            "reason": reason
        }
