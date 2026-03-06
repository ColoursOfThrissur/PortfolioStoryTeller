"""
Agentic Portfolio Report API - New Architecture
Uses Planner Agent + State Manager + Section Agents
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import uuid
from datetime import datetime

from core.orchestrator import orchestrator

app = FastAPI(title="Agentic Portfolio Report API v2")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check"""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "status": "healthy",
        "service": "agentic-backend-v2",
        "architecture": "planner + state + agents",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }


@app.post("/api/session/create")
async def create_session():
    """Create new report generation session"""
    session_id = orchestrator.create_session()
    return {
        "session_id": session_id,
        "created_at": datetime.now().isoformat()
    }


@app.get("/api/session/{session_id}")
async def get_session_status(session_id: str):
    """Get session status"""
    status = await orchestrator.get_session_status(session_id)
    if not status["exists"]:
        raise HTTPException(status_code=404, detail="Session not found")
    return status


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload portfolio file"""
    try:
        # Save to temp directory in agentic-backend
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        
        with file_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "success": True,
            "file_path": str(file_path.absolute()),
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for chat interface"""
    await websocket.accept()
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to agentic report generator. How can I help you today?",
            "session_id": session_id
        })
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data["type"] == "message":
                user_message = data["content"]
                uploaded_file = data.get("file_path")
                
                # Process through orchestrator
                response = await orchestrator.handle_message(
                    session_id,
                    user_message,
                    uploaded_file
                )
                
                # Send response
                await websocket.send_json(response)
            
            elif data["type"] == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Error: {str(e)}"
        })


@app.post("/api/chat/{session_id}")
async def chat_http(session_id: str, message: dict):
    """HTTP endpoint for chat (alternative to WebSocket)"""
    try:
        user_message = message.get("content", "")
        uploaded_file = message.get("file_path")
        
        response = await orchestrator.handle_message(
            session_id,
            user_message,
            uploaded_file
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
