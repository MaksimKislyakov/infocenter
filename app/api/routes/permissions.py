from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, require_admin
from app.repositories.permission_repository import PermissionRepository
from app.repositories.unit_repository import UnitRepository
from app.services.permission_service import PermissionService
from app.schemas.permission_schema import (
    PermissionGrantSchema,
    PermissionResponseSchema,
    UserPermissionsRequestSchema,
)

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/users/{user_id}", response_model=list[PermissionResponseSchema])
def grant_user_permissions(
    user_id: UUID,
    data: UserPermissionsRequestSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Массовая выдача прав пользователю (админ)"""
    service = PermissionService(db)
    granted = service.grant_bulk(user_id, data)
    return [PermissionResponseSchema.model_validate(p) for p in granted]


@router.delete("/users/{user_id}")
def revoke_user_permissions(
    user_id: UUID,
    permissions: list[PermissionGrantSchema],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Массовый отзыв прав"""
    service = PermissionService(db)
    count = service.revoke_bulk(user_id, permissions)
    return {"revoked": count}


@router.get("/users/{user_id}", response_model=list[PermissionResponseSchema])
def get_user_permissions(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Получить все права пользователя"""
    repo = PermissionRepository(db)
    perms = repo.get_user_permissions(user_id)
    return [
        PermissionResponseSchema(
            id=p.id,
            unit_id=p.unit_id,
            unit_name=p.unit.name,
            unit_level=p.unit.level_type,
            block=p.block,
            action=p.action,
        )
        for p in perms
    ]


@router.get("/units/tree")
def get_units_tree(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Получить дерево подразделений для админки"""
    repo = UnitRepository(db)
    return repo.get_tree()