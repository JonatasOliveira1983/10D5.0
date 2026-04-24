# 1CRYPTEN_SPACE_V4.0 - V110.175 WebSocket Service (Real-time Command Center)
import logging
import json
import asyncio
from typing import List, Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("WebSocketService")

class WebSocketService:
    def __init__(self):
        # Gerencia as conexões ativas do Cockpit
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🔌 Cockpit Connected. Active sessions: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"❌ Cockpit Disconnected. Active sessions: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Envia dados para todos os cockpits conectados."""
        if not self.active_connections:
            return
            
        disconnected = set()
        msg_str = json.dumps(message)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(msg_str)
            except Exception as e:
                logger.warning(f"Failed to send WS message: {e}")
                disconnected.add(connection)
        
        # Cleanup
        for conn in disconnected:
            self.disconnect(conn)

    async def emit_slot_update(self, slot_id: int, data: dict):
        """Envia atualização de um slot específico."""
        await self.broadcast({
            "type": "SLOT_UPDATE",
            "slot_id": slot_id,
            "data": data
        })

    async def emit_radar_pulse(self, signals: list):
        """Envia novos sinais do Radar."""
        await self.broadcast({
            "type": "RADAR_PULSE",
            "signals": signals
        })

    async def emit_banca_status(self, data: dict):
        """Envia status da banca."""
        await self.broadcast({
            "type": "BANCA_STATUS",
            "data": data
        })

websocket_service = WebSocketService()
