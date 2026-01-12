"""FastAPI backend for AI Foundry Customer Support Demo.

This module provides the REST API endpoints for the multi-agent
customer support system using Azure AI Foundry Agent Service.
"""

import os
import uuid
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.orchestrator import AgentOrchestrator
from services.cosmos_service import CosmosService
from services.search_service import SearchService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
orchestrator: AgentOrchestrator = None
cosmos_service: CosmosService = None
search_service: SearchService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global orchestrator, cosmos_service, search_service
    
    logger.info("Initializing services...")
    
    # Initialize services
    cosmos_service = CosmosService()
    search_service = SearchService()
    orchestrator = AgentOrchestrator(
        cosmos_service=cosmos_service,
        search_service=search_service
    )
    
    await orchestrator.initialize()
    logger.info("Services initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")


app = FastAPI(
    title="AI Foundry Customer Support API",
    description="Multi-agent customer support system for consumer goods",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str
    response: str
    agent: str
    thought_process: list[dict] | None = None


class SessionResponse(BaseModel):
    """Response model for new session."""
    session_id: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "customer-support-api"}


@app.post("/api/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    await cosmos_service.create_session(session_id)
    return SessionResponse(session_id=session_id)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the agent orchestrator."""
    try:
        # Create session if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process message through orchestrator
        result = await orchestrator.process_message(
            session_id=session_id,
            message=request.message
        )
        
        return ChatResponse(
            session_id=session_id,
            response=result["response"],
            agent=result["agent"],
            thought_process=result.get("thought_process")
        )
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response for real-time UI updates."""
    session_id = request.session_id or str(uuid.uuid4())
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            async for chunk in orchestrator.process_message_stream(
                session_id=session_id,
                message=request.message
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    try:
        history = await cosmos_service.get_conversation_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products")
async def get_products():
    """Get list of products for the catalog."""
    try:
        products = await search_service.get_all_products()
        return {"products": products}
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details by order ID."""
    try:
        order = await cosmos_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
