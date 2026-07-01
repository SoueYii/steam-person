from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.analytics_service import realtime_players
import asyncio
import json
import logging

logger = logging.getLogger("steam.ws")

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WS error: {e}")
        manager.disconnect(ws)


async def broadcast_players():
    """定时广播在线玩家数据"""
    while True:
        try:
            data = realtime_players(20)
            await manager.broadcast({"type": "realtime_players", "data": data})
        except Exception as e:
            logger.error(f"广播失败: {e}")
        await asyncio.sleep(60)
