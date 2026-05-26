from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import decode_refresh_token
from app.repositories.user_repositoriy import UserRepository
from app.schemas.auth_schema import LoginRequest, RefreshTokenRequest, Token
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Авторизация пользователя.

    Возвращает:
    - access_token: JWT токен для API запросов (заголовок Authorization: Bearer {token})
    - refresh_token: Токен для обновления access_token'а
    - token_type: Тип токена (всегда "bearer")
    """
    user = authenticate_user(db, form_data.login, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.login})
    refresh_token = create_refresh_token(data={"sub": user.login})

    repo = UserRepository(db)
    repo.update_refresh_token(user, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Обновить access_token используя refresh_token.

    Возвращает новую пару:
    - access_token: Новый JWT токен
    - refresh_token: Новый refresh токен
    - token_type: "bearer"
    """
    payload = decode_refresh_token(request.refresh_token)
    login: str | None = payload.get("sub")
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    repo = UserRepository(db)
    user = repo.get_by_login(login)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(data={"sub": user.login})
    refresh_token = create_refresh_token(data={"sub": user.login})

    repo.update_refresh_token(user, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
