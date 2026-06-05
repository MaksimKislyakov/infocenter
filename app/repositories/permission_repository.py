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
        existing = (
            self.db.query(UserUnitPermission)
            .filter(
                UserUnitPermission.user_id == user_id,
                UserUnitPermission.unit_id == perm.unit_id,
                UserUnitPermission.block == perm.block,
                UserUnitPermission.action == perm.action,
            )
            .first()
        )
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
        target = (
            self.db.query(UserUnitPermission)
            .filter(
                UserUnitPermission.user_id == user_id,
                UserUnitPermission.unit_id == perm.unit_id,
                UserUnitPermission.block == perm.block,
                UserUnitPermission.action == perm.action,
            )
            .first()
        )
        if not target:
            return False
        self.db.delete(target)
        self.db.commit()
        return True

    def grant_bulk(
        self, user_id: UUID, permissions: list[PermissionGrantSchema]
    ) -> list[UserUnitPermission]:
        """Добавляет новые права пользователю, не удаляя существующие."""
        existing_perms = (
            self.db.query(UserUnitPermission)
            .filter(UserUnitPermission.user_id == user_id)
            .all()
        )
        existing_map = {
            (perm.unit_id, perm.block, perm.action): perm
            for perm in existing_perms
        }

        perms_to_add: list[UserUnitPermission] = []
        for perm in permissions:
            key = (perm.unit_id, perm.block, perm.action)
            if key not in existing_map:
                new_perm = UserUnitPermission(
                    user_id=user_id,
                    unit_id=perm.unit_id,
                    block=perm.block,
                    action=perm.action,
                )
                perms_to_add.append(new_perm)
                existing_map[key] = new_perm

        if perms_to_add:
            self.db.add_all(perms_to_add)
            self.db.commit()
            for perm in perms_to_add:
                self.db.refresh(perm)
            existing_perms.extend(perms_to_add)

        return existing_perms

    def revoke_bulk(
        self, user_id: UUID, permissions: list[PermissionGrantSchema]
    ) -> int:
        """Массовый отзыв прав (с одним commit для всех)"""
        to_delete = []

        for perm in permissions:
            target = (
                self.db.query(UserUnitPermission)
                .filter(
                    UserUnitPermission.user_id == user_id,
                    UserUnitPermission.unit_id == perm.unit_id,
                    UserUnitPermission.block == perm.block,
                    UserUnitPermission.action == perm.action,
                )
                .first()
            )
            if target:
                to_delete.append(target)

        # Удаляем все права и делаем один commit
        count = 0
        if to_delete:
            for target in to_delete:
                self.db.delete(target)
            self.db.commit()
            count = len(to_delete)

        return count

    def get_user_permissions(self, user_id: UUID) -> list[UserUnitPermission]:
        """Получить все права пользователя с данными подразделений"""
        return (
            self.db.query(UserUnitPermission)
            .options(joinedload(UserUnitPermission.unit))
            .filter(UserUnitPermission.user_id == user_id)
            .all()
        )

    def check_direct_permission(
        self, user_id: UUID, unit_id: UUID, block: Block, action: Action
    ) -> bool:
        """Проверка прямого права (без наследования)"""
        action_filter = [action]
        if action == Action.VIEW:
            action_filter = [Action.VIEW, Action.MANAGE]

        return (
            self.db.query(UserUnitPermission.id)
            .filter(
                UserUnitPermission.user_id == user_id,
                UserUnitPermission.unit_id == unit_id,
                UserUnitPermission.block.in_([block, Block.ALL]),
                UserUnitPermission.action.in_(action_filter),
            )
            .first()
            is not None
        )
