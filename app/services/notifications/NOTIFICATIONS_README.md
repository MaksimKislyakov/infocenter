# Система уведомлений (Notifications System)

## Обзор

Система уведомлений позволяет в реальном времени отправлять уведомления пользователям через WebSocket. Архитектура спроектирована для простого расширения под различные типы уведомлений.

## Компоненты

### 1. **NotificationManager** (`notification_service.py`)
Центральный менеджер для управления WebSocket-соединениями и отправки уведомлений.

**Основные методы:**
- `connect(user_id: str, websocket: WebSocket)` — подключить пользователя
- `disconnect(user_id: str, websocket: WebSocket)` — отключить пользователя
- `send_personal_message(user_id: str, payload: NotificationPayload)` — отправить персональное уведомление
- `broadcast(payload: NotificationPayload)` — отправить уведомление всем подключённым пользователям
- `notify_diagram_updated(...)` — специализированный метод для уведомлений об обновлении диаграммы

**Глобальный экземпляр:**
```python
from app.services.notification_service import notification_manager
```

### 2. **NotificationPayload** (`schemas/notification_schema.py`)
Pydantic-модель для структурирования уведомления.

```python
class NotificationPayload(BaseModel):
    type: NotificationType              # Тип уведомления (enum)
    recipient_id: str                  # ID получателя
    actor_id: str                      # ID пользователя, который сделал действие
    diagram_id: str                    # ID диаграммы (зависит от типа уведомления)
    message: str                       # Человеко-читаемое сообщение
    data: dict | None = None          # Дополнительные данные
    timestamp: datetime                # Время создания
```

### 3. **WebSocket Route** (`api/routes/notifications.py`)
Маршрут для подключения пользователей к WebSocket.

```python
@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, current_user=Depends(get_current_user_ws)):
    # Автоматически управляется менеджером
```

## Как добавить новый тип уведомления

### Шаг 1: Добавить тип в `NotificationType` enum
**Файл:** `app/schemas/notification_schema.py`

```python
class NotificationType(str, Enum):
    diagram_updated = "diagram_updated"
    chart_updated = "chart_updated"        # Новый тип
    permission_granted = "permission_granted"  # Ещё один пример
```

### Шаг 2: Добавить метод в `NotificationManager`
**Файл:** `app/services/notification_service.py`

```python
async def notify_chart_updated(
    self,
    recipient_id: str,
    actor_id: str,
    chart_id: str,
    message: str | None = None,
) -> None:
    payload = NotificationPayload(
        type="chart_updated",
        recipient_id=recipient_id,
        actor_id=actor_id,
        diagram_id=chart_id,  # Переиспользуем diagram_id для ID ресурса
        message=message or "График был обновлен",
        data={"chart_id": chart_id},
    )
    await self.send_personal_message(recipient_id, payload)
```

### Шаг 3: Интегрировать в маршрут или сервис
**Пример:** `app/api/routes/charts.py`

```python
@router.patch("/{chart_id}", response_model=ChartResponse)
async def update_chart(
    chart_id: int,
    data: ChartUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # ... логика обновления ...
    
    # Отправить уведомление
    if str(chart.creator_id) != str(current_user.id):
        await notification_manager.notify_chart_updated(
            recipient_id=str(chart.creator_id),
            actor_id=str(current_user.id),
            chart_id=str(chart.id),
            message=f"График {chart.title} был обновлен",
        )
    
    return chart
```

## Примеры использования на фронтенде

### Подключение к WebSocket

```javascript
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?token=${token}`);

ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    
    if (notification.type === "diagram_updated") {
        console.log(`Диаграмма ${notification.diagram_id} была обновлена`);
        console.log(`Автор изменения: ${notification.actor_id}`);
        console.log(`Сообщение: ${notification.message}`);
    }
    
    if (notification.type === "chart_updated") {
        console.log(`График был обновлен: ${notification.data.chart_id}`);
    }
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};

ws.onclose = () => {
    console.log("WebSocket соединение закрыто");
};
```

## Тестирование

Смотрите `tests/test_notifications.py` для примеров unit-тестов:

```bash
poetry run pytest -q tests/test_notifications.py -v
```

**Основные тесты:**
- `test_notification_manager_stores_connections` — проверка управления соединениями
- `test_notification_payload_creation` — валидация формата уведомления
- `test_notification_manager_send_personal_message` — отправка персональных сообщений
- `test_diagram_update_notification` — полный цикл уведомления об обновлении диаграммы

## Архитектурные рекомендации

### Масштабируемость
Для масштабирования на несколько серверов используйте Redis pub/sub вместо in-memory хранилища:

```python
# Будущее улучшение
class RedisNotificationManager(NotificationManager):
    def __init__(self, redis_client):
        super().__init__()
        self.redis = redis_client
    
    async def broadcast(self, payload: NotificationPayload):
        # Публиковать в Redis для распределения на другие серверы
        await self.redis.publish("notifications", payload.model_dump_json())
```

### Типизация
Используйте TypedDict для расширенных `data` в уведомлениях:

```python
from typing import TypedDict

class DiagramUpdatedData(TypedDict):
    diagram_id: str
    changed_fields: list[str]

# В методе:
data: DiagramUpdatedData = {
    "diagram_id": diagram_id,
    "changed_fields": ["order", "rows"]
}
```

### Обработка ошибок
Менеджер автоматически отключает WebSocket при ошибке отправки. Для более сложной логики переопределите `send_personal_message`.

## Миграция к другим системам

Система изолирована и легко заменяется на:
- **AWS SNS/SQS** — добавьте AsyncAWSClient в менеджер
- **Firebase Cloud Messaging** — создайте `FirebaseNotificationManager`
- **Socket.IO** — замените FastAPI WebSocket на Socket.IO сервер
- **Kafka** — добавьте Kafka producer для асинхронной обработки
