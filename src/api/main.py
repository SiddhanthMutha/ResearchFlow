"""FastAPI server for the Multi-Agent Research Assistant."""

import uuid
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.graph.workflow import run_research
from src.memory.storage import storage
from src.api.websocket import ws_manager
from src.utils.config import config
from src.utils.cost_tracker import cost_tracker, estimate_tokens


# Request/Response models
class ResearchRequest(BaseModel):
    question: str
    use_wikipedia: bool = True


class ResearchResponse(BaseModel):
    id: str
    status: str
    message: str


class ResearchResult(BaseModel):
    id: str
    query: str
    final_answer: str
    sources: List[Dict[str, str]]
    cost: float
    duration_seconds: float
    status: str
    created_at: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await storage.initialize()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="AI-powered research assistant with multiple specialized agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket endpoint
@app.websocket("/ws/{research_id}")
async def websocket_endpoint(websocket: WebSocket, research_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await ws_manager.connect(websocket, research_id)
    try:
        while True:
            # Keep connection alive, wait for messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, research_id)


# API Endpoints
@app.post("/research", response_model=ResearchResponse)
async def create_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a new research query.
    
    The research will run in the background and progress can be tracked via WebSocket.
    """
    research_id = str(uuid.uuid4())
    
    # Start research in background
    background_tasks.add_task(
        run_research_task,
        research_id,
        request.question,
        request.use_wikipedia
    )
    
    return ResearchResponse(
        id=research_id,
        status="started",
        message="Research task started. Connect to /ws/{research_id} for progress updates."
    )


async def run_research_task(research_id: str, question: str, use_wikipedia: bool):
    """Run research task in background and update progress."""
    start_time = time.time()
    
    try:
        # Send initial progress
        await ws_manager.send_progress(
            research_id,
            "CoordinatorAgent",
            "started",
            "Starting research task...",
            0.0
        )
        
        # Run the research
        result = run_research(question)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Estimate cost
        estimated_tokens = (
            estimate_tokens(question) +
            estimate_tokens(result.get("final_answer", ""))
        )
        estimated_cost = cost_tracker.get_total_cost()
        
        # Save to database
        await storage.save_research(
            research_id=research_id,
            query=question,
            clarified_query=result.get("clarified_question", question),
            final_answer=result.get("final_answer", ""),
            sources=result.get("sources", []),
            cost=estimated_cost,
            duration_seconds=duration,
            status=result.get("status", "completed")
        )
        
        # Send completion message
        await ws_manager.send_complete(
            research_id,
            result.get("final_answer", "")
        )
        
    except Exception as e:
        # Print error for debugging
        import traceback
        print(f"[ERROR] Research task failed: {e}")
        traceback.print_exc()
        # Send error message
        await ws_manager.send_error(
            research_id,
            str(e)
        )


@app.get("/research/history", response_model=List[ResearchResult])
async def get_research_history(limit: int = 20, offset: int = 0):
    """List past research queries."""
    results = await storage.get_research_history(limit, offset)
    
    return [
        ResearchResult(
            id=r["id"],
            query=r["query"],
            final_answer=r["final_answer"],
            sources=[],
            cost=r["cost"],
            duration_seconds=r["duration_seconds"],
            status=r["status"],
            created_at=r["created_at"]
        )
        for r in results
    ]


@app.get("/research/{research_id}", response_model=ResearchResult)
async def get_research(research_id: str):
    """Get results of a completed research query."""
    result = await storage.get_research(research_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Research not found")
    
    return ResearchResult(
        id=result["id"],
        query=result["query"],
        final_answer=result["final_answer"],
        sources=eval(result["sources"]) if isinstance(result["sources"], str) else result["sources"],
        cost=result["cost"],
        duration_seconds=result["duration_seconds"],
        status=result["status"],
        created_at=result["created_at"]
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Multi-Agent Research Assistant",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
