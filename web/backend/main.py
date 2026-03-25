import sys
import os
import json
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from soul.brain import Soul
from soul.identity import PROFILE
from soul.state import state_machine
from soul.event_loop import AutonomousLoop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ANDILE_WEB")

app = FastAPI(title="Andile Digital Twin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

soul = None
event_loop = None
eyes = None


@app.on_event("startup")
async def startup_event():
    global soul, event_loop, eyes
    logger.info("Initializing Andile's Soul...")
    soul = Soul(name="Andile Sizophila Mchunu")
    logger.info("Soul initialized.")

    # Initialize vision (lazy — only if packages installed)
    try:
        from soul.vision.eyes import Eyes

        eyes = Eyes()
        logger.info("Vision system ready")
    except Exception as e:
        logger.warning(f"Vision not available: {e}")
        eyes = None

    # Start Autonomous Event Loop
    event_loop = AutonomousLoop(soul)
    asyncio.create_task(event_loop.start())
    logger.info("Autonomous loop dispatched to background.")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    status: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not soul:
        raise HTTPException(status_code=503, detail="Soul not initialized")
    try:
        response = await soul.perceive(request.message)
        return ChatResponse(response=response, status="success")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    if not soul:
        return {"status": "initializing"}
    status_str = soul.status()
    return {
        "raw_status": status_str,
        "interactions": soul.interaction_count,
        "memories": soul.memory.count(),
        "uptime": soul.clock.session_duration(),
    }


@app.get("/identity")
async def get_identity():
    return PROFILE


@app.get("/history")
async def get_history():
    if not soul:
        return []
    return soul.memory.get_recent_conversation(n=20)


@app.get("/state")
async def get_state():
    return state_machine.data


@app.get("/actions")
async def get_actions():
    if not soul:
        return []
    return soul.memory.recall("recent actions", n=10)


# === VISION ENDPOINTS ===


@app.get("/vision/capture")
async def vision_capture():
    """Capture and analyze current screen."""
    if not eyes:
        return {"error": "Vision not available", "text": "", "summary": ""}

    try:
        vision = eyes.see()
        result = {
            "text": vision.get("text", ""),
            "summary": vision.get("summary", ""),
            "screen_size": vision.get("screen_size"),
            "text_boxes": len(vision.get("text_boxes", [])),
            "timestamp": vision.get("timestamp"),
        }

        # Save to memory
        if soul and vision.get("text"):
            soul.memory.store(
                "vision",
                f"Screen captured: {vision['text'][:200]}",
                importance=0.5,
            )

        return result
    except Exception as e:
        logger.error(f"Vision capture failed: {e}")
        return {"error": str(e), "text": "", "summary": ""}


@app.get("/vision/status")
async def vision_status():
    """Get vision system status."""
    if not eyes:
        return {"available": False}
    return {"available": True, **eyes.get_state()}


@app.get("/vision/screenshot")
async def vision_screenshot():
    """Take a screenshot and return as base64."""
    if not eyes:
        return {"error": "Vision not available"}

    try:
        import cv2
        import numpy as np
        from soul.vision.screen import ScreenCapture

        sc = ScreenCapture()
        img = sc.capture()
        if img is None:
            return {"error": "Capture failed"}

        # Convert to base64 PNG
        _, buffer = cv2.imencode(".png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        b64 = base64.b64encode(buffer).decode()

        return {
            "image": f"data:image/png;base64,{b64}",
            "width": img.shape[1],
            "height": img.shape[0],
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
