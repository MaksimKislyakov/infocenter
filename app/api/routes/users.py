from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db, require_admin
from app.core.enums import Role
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate, ChangePasswordSchema
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Создать нового пользователя (только админ).
    
    Пароль будет сгенерирован автоматически и отправлен на электронную почту пользователя.
    Администратор не может узнать пароль - он известен только пользователю.

    **Role (роль пользователя):**
    - user: Пользователь (просмотр)
    - admin: Администратор (полный доступ)
    """
    service = UserService(db)
    try:
        return service.create_user(user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Получить список всех пользователей (только админ)."""
    return UserService(db).list_users()


@router.get("/me", response_model=UserRead)
def read_current_user(current_user=Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе."""
    return current_user


@router.patch("/me/password")
def change_password(
    password_data: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Пользователь меняет свой пароль.
    
    Требуется ввод текущего пароля для подтверждения.
    """
    service = UserService(db)
    success = service.change_password(
        str(current_user.id),
        password_data.current_password,
        password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Current password may be incorrect."
        )
    return {"detail": "Password changed successfully"}


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: UUID,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Сброс пароля пользователя (только админ).
    
    Генерирует новый пароль и отправляет его на электронную почту пользователя.
    Старый пароль становится недействительным.
    
    **Требования:**
    - У пользователя должен быть установлен email адрес
    """
    service = UserService(db)
    success = service.reset_password(str(user_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password. User not found or has no email."
        )
    return {"detail": "Password reset successfully. New password sent to user's email."}


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Получить информацию о пользователе (админ или сам пользователь)."""
    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges"
        )
    user = UserService(db).get_by_id(str(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Обновить данные пользователя (только админ).
    
    Смена пароля не поддерживается через этот эндпоинт.
    Используйте POST /{user_id}/reset-password для сброса пароля.
    """
    service = UserService(db)
    try:
        user = service.update_user(str(user_id), user_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Удалить пользователя (только админ)."""
    deleted = UserService(db).delete_user(str(user_id))
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"detail": "User deleted"}
