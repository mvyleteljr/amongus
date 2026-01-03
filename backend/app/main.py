"""FastAPI application for LLM Among Us."""

import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .models import CreateGameRequest, GameStateResponse
from .game import game_manager


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def broadcast(self, game_id: str, message: dict):
        if game_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)
            for conn in dead_connections:
                self.disconnect(conn, game_id)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="LLM Among Us",
    description="A game where LLMs compete in programming tasks with one imposter",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "LLM Among Us API", "version": "1.0.0"}


@app.post("/api/game/create")
async def create_game(request: CreateGameRequest):
    """Create a new game."""
    try:
        game = game_manager.create_game(request.models)
        return game_manager.get_game_response(game.gameId)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/game/{game_id}/start")
async def start_game(game_id: str):
    """Start a game."""
    game = game_manager.start_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or already started")

    response = game_manager.get_game_response(game_id)
    await manager.broadcast(game_id, {"type": "game_state_update", "data": response.model_dump()})
    return response


@app.get("/api/game/{game_id}/state")
async def get_game_state(game_id: str):
    """Get current game state."""
    response = game_manager.get_game_response(game_id)
    if not response:
        raise HTTPException(status_code=404, detail="Game not found")
    return response


@app.post("/api/game/{game_id}/advance")
async def advance_phase(game_id: str):
    """Advance to the next game phase."""
    game = await game_manager.advance_phase(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or not in progress")

    response = game_manager.get_game_response(game_id)
    await manager.broadcast(
        game_id,
        {
            "type": "game_state_update",
            "data": response.model_dump(),
        },
    )
    return response


@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    """Delete a game."""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game_manager.delete_game(game_id)
    return {"message": "Game deleted"}


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for real-time game updates."""
    game = game_manager.get_game(game_id)
    if not game:
        await websocket.close(code=4004, reason="Game not found")
        return

    await manager.connect(websocket, game_id)
    try:
        # Send current state on connect
        response = game_manager.get_game_response(game_id)
        await websocket.send_json({"type": "game_state_update", "data": response.model_dump()})

        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
    except Exception:
        manager.disconnect(websocket, game_id)
