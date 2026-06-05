import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[WebSocket, dict] = {}  # ws -> {symbols, channels}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = {"symbols": set(), "channels": set()}

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.subscriptions.pop(websocket, None)

    async def send_json(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except Exception:
            self.disconnect(websocket)


manager = ConnectionManager()


@router.websocket("/ws/quote")
async def websocket_quote(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "subscribe":
                symbols = set(data.get("symbols", []))
                channels = set(data.get("channels", []))
                if websocket in manager.subscriptions:
                    manager.subscriptions[websocket]["symbols"].update(symbols)
                    manager.subscriptions[websocket]["channels"].update(channels)
                await manager.send_json(websocket, {"action": "subscribed", "symbols": list(symbols), "channels": list(channels)})

            elif action == "unsubscribe":
                symbols = set(data.get("symbols", []))
                if websocket in manager.subscriptions:
                    manager.subscriptions[websocket]["symbols"] -= symbols

            elif action == "ping":
                await manager.send_json(websocket, {"action": "pong", "timestamp": __import__("datetime").datetime.now().isoformat()})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_quote_update(symbol: str, quote_data: dict):
    """广播行情更新到订阅了该股票的客户端"""
    message = {"type": "quote", "symbol": symbol, "data": quote_data}
    disconnected = []
    for ws in manager.active_connections:
        sub = manager.subscriptions.get(ws, {})
        if symbol in sub.get("symbols", set()) and "quote" in sub.get("channels", set()):
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
    for ws in disconnected:
        manager.disconnect(ws)