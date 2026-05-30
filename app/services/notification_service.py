import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationPayload, NotificationType

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

    async def send_personal_message(
        self,
        user_id: str,
        payload: NotificationPayload,
    ) -> bool:
        if user_id not in self.active_connections:
            logger.debug("No active WS connections for user=%s", user_id)
            return False

        message = jsonable_encoder(payload)
        logger.debug(
            "Sending notification to user=%s payload_type=%s",
            user_id,
            payload.type,
        )

        sent = False
        for websocket in list(self.active_connections[user_id]):
            try:
                await websocket.send_json(message)
                sent = True
            except Exception as exc:
                logger.exception(
                    "Failed to send notification to user=%s: %s",
                    user_id,
                    exc,
                )
                self.disconnect(user_id, websocket)
        return sent

    async def broadcast(self, payload: NotificationPayload) -> None:
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, payload)

    async def send_pending_notifications(self, user_id: str, db: Session) -> int:
        repo = NotificationRepository(db)
        pending_notifications = repo.get_pending_notifications(user_id)
        logger.debug(
            "Sending pending notifications for user=%s count=%s",
            user_id,
            len(pending_notifications),
        )

        delivered_count = 0
        for notification in pending_notifications:
            payload = NotificationPayload(
                type=notification.type,
                recipient_id=str(notification.recipient_id),
                actor_id=str(notification.actor_id),
                diagram_id=str(notification.diagram_id),
                message=notification.message,
                data=notification.data,
                timestamp=notification.created_at,
            )
            sent = await self.send_personal_message(user_id, payload)
            if sent:
                repo.mark_as_delivered(notification)
                logger.debug(
                    "Delivered pending notification id=%s user=%s",
                    notification.id,
                    user_id,
                )
                delivered_count += 1
            else:
                logger.debug(
                    "Pending notification id=%s user=%s not delivered yet",
                    notification.id,
                    user_id,
                )

        return delivered_count

    async def notify_diagram_updated(
        self,
        recipient_id: str,
        actor_id: str,
        diagram_id: str,
        message: str | None = None,
        db: Session | None = None,
    ) -> None:
        notification = None
        repo = None
        if db is not None:
            repo = NotificationRepository(db)
            notification = repo.create_notification(
                recipient_id=recipient_id,
                actor_id=actor_id,
                diagram_id=diagram_id,
                message=message or "Диаграмма была обновлена",
                data={"diagram_id": diagram_id},
                type=NotificationType.diagram_updated,
            )
            logger.debug(
                "Created notification id=%s recipient=%s actor=%s diagram=%s",
                notification.id,
                recipient_id,
                actor_id,
                diagram_id,
            )

        payload = NotificationPayload(
            type=NotificationType.diagram_updated,
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

        delivered = await self.send_personal_message(recipient_id, payload)
        if delivered and repo is not None and notification is not None:
            repo.mark_as_delivered(notification)
            logger.debug(
                "Delivered new notification id=%s immediately",
                notification.id,
            )


notification_manager = NotificationManager()
