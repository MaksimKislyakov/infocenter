from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_user_ws, get_db
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationResponse
from app.services.notifications.notification_service import notification_manager

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    current_user=Depends(get_current_user_ws),
    db: Session = Depends(get_db),
):
    user_id = str(current_user.id)
    await notification_manager.connect(user_id, websocket)
    try:
        await notification_manager.send_pending_notifications(user_id, db)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(user_id, websocket)


@router.get("/notifications/pending")
def get_pending_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Получить неполученные уведомления, накопившиеся во время отсутствия пользователя.
    """
    notifications_repo = NotificationRepository(db)
    pending_notifications = notifications_repo.mark_pending_as_delivered(str(current_user.id))

    return [
        {
            "id": str(notification.id),
            "type": notification.type,
            "recipient_id": str(notification.recipient_id),
            "actor_id": str(notification.actor_id),
            "diagram_id": str(notification.diagram_id),
            "message": notification.message,
            "data": notification.data,
            "timestamp": notification.created_at,
            "delivered_at": notification.delivered_at,
        }
        for notification in pending_notifications
    ]


@router.get("/notifications", response_model=list[NotificationResponse])
def get_all_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Получить всю историю уведомлений для текущего пользователя.
    """
    notifications_repo = NotificationRepository(db)
    notifications = notifications_repo.get_user_notifications(str(current_user.id))

    return [
        {
            "id": str(notification.id),
            "type": notification.type,
            "recipient_id": str(notification.recipient_id),
            "actor_id": str(notification.actor_id),
            "diagram_id": str(notification.diagram_id),
            "message": notification.message,
            "data": notification.data,
            "timestamp": notification.created_at,
            "delivered_at": notification.delivered_at,
        }
        for notification in notifications
    ]
