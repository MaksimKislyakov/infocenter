from pydantic import BaseModel

from app.schemas.notification_schema import NotificationResponse


class LoginRequest(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenWithNotifications(Token):
    notifications: list[NotificationResponse] = []


class TokenData(BaseModel):
    login: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
