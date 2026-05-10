from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import Role
from app.db.session import get_db
from app.repositories.user_repositoriy import UserRepository
from app.schemas.auth_schema import TokenData
from app.core.security import decode_access_token
from app.core.enums import Block, Action
from app.services.permission_service import PermissionService

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        login: str | None = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)
    except JWTError:
        raise credentials_exception

    user = UserRepository(db).get_by_login(token_data.login)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def require_admin(current_user=Depends(get_current_active_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def require_diagram_permission(action: Action, block: Block | None = None):
    """
    Зависимость для проверки доступа к диаграммам.
    Используется в роутах диаграмм.
    """
    def dep(
        current_user=Depends(get_current_active_user),
        db: Session = Depends(get_db),
        diagram_id: str | None = None,  # опционально, если нужно проверять конкретную диаграмму
    ):
        # Если глобальный админ — доступ всегда есть
        if getattr(current_user, "is_global_admin", False):
            return current_user
        
        # Для примера: если diagram_id передан, нужно получить его unit_id и block
        # Здесь упрощённо: проверяем доступ на уровне пользователя
        service = PermissionService(db)
        
        # Если block не указан — проверяем доступ к любому блоку (для списков)
        blocks_to_check = [block] if block else [b for b in Block if b != Block.ALL]
        
        # Проверяем: есть ли доступ хотя бы к одному подразделению с нужным действием
        # В реальном проекте: передавать unit_id из контекста запроса
        has_access = any(
            service.has_access(current_user.id, unit_id, b, action)
            for b in blocks_to_check
            for unit_id in []  # TODO: получить unit_id из диаграммы или запроса
        )
        
        if not has_access and not getattr(current_user, "is_global_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return current_user
    return dep