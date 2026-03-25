from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from soul.core.logger import setup_logger
from soul.core.config import identity
import json
import asyncio

logger = setup_logger(__name__)
app = FastAPI(title="Soul Control Center")

# Allow dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state shared with the event loop
system_status = {
    "state": "initializing",
    "current_task": "None",
    "last_heartbeat": 0
}

@app.get("/status")
async def get_status():
    return system_status

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Dashboard connected to Control Center WebSocket.")
    try:
        while True:
            # Send current telemetry
            await websocket.send_json(system_status)
            await asyncio.sleep(1) # Broadcast every second
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
