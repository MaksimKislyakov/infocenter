from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from uuid import UUID

from app.models.permission_model import UserUnitPermission
from app.core.enums import Block, Action
from app.schemas.permission_schema import PermissionGrantSchema


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def grant(self, user_id: UUID, perm: PermissionGrantSchema) -> UserUnitPermission:
        """Выдать одно право (идемпотентно)"""
        existing = self.db.query(UserUnitPermission).filter(
            UserUnitPermission.user_id == user_id,
            UserUnitPermission.unit_id == perm.unit_id,
            UserUnitPermission.block == perm.block,
            UserUnitPermission.action == perm.action,
        ).first()
        if existing:
            return existing
        
        new_perm = UserUnitPermission(
            user_id=user_id,
            unit_id=perm.unit_id,
            block=perm.block,
            action=perm.action,
        )
        self.db.add(new_perm)
        self.db.commit()
        self.db.refresh(new_perm)
        return new_perm

    def revoke(self, user_id: UUID, perm: PermissionGrantSchema) -> bool:
        """Отозвать право"""
        target = self.db.query(UserUnitPermission).filter(
            UserUnitPermission.user_id == user_id,
            UserUnitPermission.unit_id == perm.unit_id,
            UserUnitPermission.block == perm.block,
            UserUnitPermission.action == perm.action,
        ).first()
        if not target:
            return False
        self.db.delete(target)
        self.db.commit()
        return True

    def get_user_permissions(self, user_id: UUID) -> list[UserUnitPermission]:
        """Получить все права пользователя с данными подразделений"""
        return (
            self.db.query(UserUnitPermission)
            .options(joinedload(UserUnitPermission.unit))
            .filter(UserUnitPermission.user_id == user_id)
            .all()
        )

    def check_direct_permission(self, user_id: UUID, unit_id: UUID, block: Block, action: Action) -> bool:
        """Проверка прямого права (без наследования)"""
        return self.db.query(
            UserUnitPermission.id
        ).filter(
            UserUnitPermission.user_id == user_id,
            UserUnitPermission.unit_id == unit_id,
            UserUnitPermission.block.in_([block, Block.ALL]),
            UserUnitPermission.action == action,
        ).first() is not None