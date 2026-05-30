import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from app.schemas.notification_schema import NotificationPayload

logger = logging.getLogger("notification")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)
        logger.debug("WS connect user=%s connections=%s", user_id, len(self.active_connections[user_id]))

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id)
        if not connections:
            logger.debug("WS disconnect user=%s no connections", user_id)
            return
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(user_id, None)
        logger.debug("WS disconnect user=%s remaining=%s", user_id, len(self.active_connections.get(user_id, [])))

    async def send_personal_message(self, user_id: str, payload: NotificationPayload) -> None:
        if user_id not in self.active_connections:
            logger.debug("No active WS connections for user=%s", user_id)
            return

        message = jsonable_encoder(payload)
        logger.debug(
            "Sending notification to user=%s payload_type=%s",
            user_id,
            payload.type,
        )

        for websocket in list(self.active_connections[user_id]):
            try:
                await websocket.send_json(message)
            except Exception as exc:
                logger.exception(
                    "Failed to send notification to user=%s: %s",
                    user_id,
                    exc,
                )
                self.disconnect(user_id, websocket)

    async def broadcast(self, payload: NotificationPayload) -> None:
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, payload)

    async def notify_diagram_updated(
        self,
        recipient_id: str,
        actor_id: str,
        diagram_id: str,
        message: str | None = None,
    ) -> None:
        payload = NotificationPayload(
            type="diagram_updated",
            recipient_id=recipient_id,
            actor_id=actor_id,
            diagram_id=diagram_id,
            message=message or "Диаграмма была обновлена",
            data={"diagram_id": diagram_id},
        )
        logger.debug(
            "Notify diagram updated recipient=%s actor=%s diagram=%s",
            recipient_id,
            actor_id,
            diagram_id,
        )
        await self.send_personal_message(recipient_id, payload)


notification_manager = NotificationManager()
