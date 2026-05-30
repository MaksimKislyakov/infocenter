from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.deps import get_current_user_ws
from app.services.notification_service import notification_manager

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket, current_user=Depends(get_current_user_ws)
):
    user_id = str(current_user.id)
    await notification_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect(user_id, websocket)
