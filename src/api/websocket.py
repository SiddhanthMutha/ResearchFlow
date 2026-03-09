"""WebSocket manager for real-time progress updates."""

import json
from datetime import datetime
from typing import Dict, Any, Set, Optional
from fastapi import WebSocket


class WebSocketManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, research_id: str):
        """Connect a WebSocket client."""
        await websocket.accept()
        
        if research_id not in self.active_connections:
            self.active_connections[research_id] = set()
        
        self.active_connections[research_id].add(websocket)

    def disconnect(self, websocket: WebSocket, research_id: str):
        """Disconnect a WebSocket client."""
        if research_id in self.active_connections:
            self.active_connections[research_id].discard(websocket)
            
            # Clean up empty research IDs
            if not self.active_connections[research_id]:
                del self.active_connections[research_id]

    async def send_progress(
        self,
        research_id: str,
        agent: str,
        status: str,
        message: str,
        progress: float
    ):
        """Send progress update to all connected clients for a research ID."""
        if research_id not in self.active_connections:
            return

        data = {
            "agent": agent,
            "status": status,
            "message": message,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections[research_id]:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections[research_id].discard(connection)

    async def send_error(self, research_id: str, error: str):
        """Send error message to all connected clients."""
        if research_id not in self.active_connections:
            return

        data = {
            "agent": "",
            "status": "error",
            "message": error,
            "progress": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        for connection in self.active_connections[research_id]:
            try:
                await connection.send_json(data)
            except Exception:
                pass

    async def send_complete(self, research_id: str, final_answer: str):
        """Send completion message to all connected clients."""
        if research_id not in self.active_connections:
            return

        data = {
            "agent": "ResearchComplete",
            "status": "completed",
            "message": "Research completed successfully",
            "progress": 1.0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "final_answer": final_answer
        }

        for connection in self.active_connections[research_id]:
            try:
                await connection.send_json(data)
            except Exception:
                pass


# Singleton instance
ws_manager = WebSocketManager()
