from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification_model import Notification
from app.schemas.notification_schema import NotificationType


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        recipient_id: str,
        actor_id: str,
        diagram_id: str,
        message: str,
        data: dict | None = None,
        type: NotificationType = NotificationType.diagram_updated,
    ) -> Notification:
        notification = Notification(
            recipient_id=UUID(recipient_id),
            actor_id=UUID(actor_id),
            diagram_id=UUID(diagram_id),
            message=message,
            data=data,
            type=type,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        self._cleanup_old_notifications(recipient_id)
        return notification

    def _cleanup_old_notifications(self, recipient_id: str) -> None:
        limit = settings.NOTIFICATION_HISTORY_LIMIT
        if limit <= 0:
            return

        total = (
            self.db.query(Notification)
            .filter(Notification.recipient_id == UUID(recipient_id))
            .count()
        )
        if total <= limit:
            return

        to_delete = total - limit
        oldest_ids = [
            row[0]
            for row in (
                self.db.query(Notification.id)
                .filter(Notification.recipient_id == UUID(recipient_id))
                .order_by(Notification.created_at.asc())
                .limit(to_delete)
                .all()
            )
        ]
        if not oldest_ids:
            return

        self.db.query(Notification).filter(Notification.id.in_(oldest_ids)).delete(synchronize_session=False)
        self.db.commit()

    def get_pending_notifications(self, recipient_id: str) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(
                Notification.recipient_id == UUID(recipient_id),
                Notification.delivered_at.is_(None),
            )
            .order_by(Notification.created_at.asc())
            .all()
        )

    def mark_as_delivered(self, notification: Notification) -> Notification:
        notification.delivered_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_pending_as_delivered(self, recipient_id: str) -> list[Notification]:
        notifications = self.get_pending_notifications(recipient_id)
        for notification in notifications:
            notification.delivered_at = datetime.utcnow()
        self.db.commit()
        for notification in notifications:
            self.db.refresh(notification)
        return notifications

    def get_user_notifications(self, recipient_id: str) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.recipient_id == UUID(recipient_id))
            .order_by(Notification.created_at.desc())
            .all()
        )
