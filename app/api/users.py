from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db, require_admin
from app.core.enums import Role
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
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
    return UserService(db).list_users()


@router.get("/me", response_model=UserRead)
def read_current_user(current_user=Depends(get_current_active_user)):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    user = UserService(db).get_by_id(str(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    service = UserService(db)
    try:
        user = service.update_user(str(user_id), user_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    deleted = UserService(db).delete_user(str(user_id))
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"detail": "User deleted"}

