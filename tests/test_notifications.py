import os
import pytest
from uuid import uuid4

os.environ["TESTING"] = "true"

from app.services.notification_service import NotificationManager
from app.schemas.notification_schema import NotificationPayload


def test_notification_manager_stores_connections():
    """Test that notification manager can store and manage connections."""
    manager = NotificationManager()
    
    # Create mock WebSocket
    class MockWebSocket:
        def __init__(self):
            self.messages = []
            
        async def send_json(self, data):
            self.messages.append(data)
    
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    
    # Test adding connections
    user1_id = str(uuid4())
    user2_id = str(uuid4())
    
    # Simulate connection
    assert user1_id not in manager.active_connections
    assert user2_id not in manager.active_connections
    
    # Manually add connections for testing
    manager.active_connections[user1_id] = [ws1]
    manager.active_connections[user2_id] = [ws2]
    
    assert len(manager.active_connections) == 2
    assert ws1 in manager.active_connections[user1_id]
    assert ws2 in manager.active_connections[user2_id]


@pytest.mark.asyncio
async def test_notification_payload_creation():
    """Test that notification payloads are created correctly."""
    manager = NotificationManager()
    
    owner_id = str(uuid4())
    admin_id = str(uuid4())
    diagram_id = str(uuid4())
    
    # Create a test payload
    payload = NotificationPayload(
        type="diagram_updated",
        recipient_id=owner_id,
        actor_id=admin_id,
        diagram_id=diagram_id,
        message="Диаграмма была обновлена",
        data={"diagram_id": diagram_id},
    )
    
    assert payload.type == "diagram_updated"
    assert payload.recipient_id == owner_id
    assert payload.actor_id == admin_id
    assert payload.diagram_id == diagram_id
    assert payload.message == "Диаграмма была обновлена"
    
    # Check serialization
    data = payload.model_dump()
    assert data["type"] == "diagram_updated"
    assert data["recipient_id"] == owner_id


@pytest.mark.asyncio
async def test_notification_manager_send_personal_message():
    """Test that notification manager can send personal messages."""
    manager = NotificationManager()
    
    class MockWebSocket:
        def __init__(self):
            self.messages = []
            self.closed = False
            
        async def send_json(self, data):
            if not self.closed:
                self.messages.append(data)
    
    ws = MockWebSocket()
    user_id = str(uuid4())
    admin_id = str(uuid4())
    diagram_id = str(uuid4())
    manager.active_connections[user_id] = [ws]
    
    # Send notification
    payload = NotificationPayload(
        type="diagram_updated",
        recipient_id=user_id,
        actor_id=admin_id,
        diagram_id=diagram_id,
        message="Test message",
        data={},
    )
    
    await manager.send_personal_message(user_id, payload)
    
    assert len(ws.messages) == 1
    assert ws.messages[0]["type"] == "diagram_updated"
    assert ws.messages[0]["recipient_id"] == user_id


@pytest.mark.asyncio  
async def test_diagram_update_notification():
    """Test the diagram update notification method."""
    manager = NotificationManager()
    
    class MockWebSocket:
        def __init__(self):
            self.messages = []
            
        async def send_json(self, data):
            self.messages.append(data)
    
    ws = MockWebSocket()
    owner_id = str(uuid4())
    admin_id = str(uuid4())
    diagram_id = str(uuid4())
    manager.active_connections[owner_id] = [ws]
    
    # Send diagram update notification
    await manager.notify_diagram_updated(
        recipient_id=owner_id,
        actor_id=admin_id,
        diagram_id=diagram_id,
        message="Test diagram update",
    )
    
    assert len(ws.messages) == 1
    message = ws.messages[0]
    assert message["type"] == "diagram_updated"
    assert message["recipient_id"] == owner_id
    assert message["actor_id"] == admin_id
    assert message["diagram_id"] == diagram_id
    assert message["message"] == "Test diagram update"
