from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.permission_repository import PermissionRepository
from app.repositories.unit_repository import UnitRepository 
from app.models.unit_model import Unit
from app.core.enums import Block, Action, OrgLevel, Role
from app.models.user_model import User
from app.schemas.permission_schema import (
    PermissionGrantSchema,
    UserPermissionsRequestSchema,
)


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.perm_repo = PermissionRepository(db)
        self.unit_repo = UnitRepository(db)

    def grant_bulk(self, user_id: UUID, data: UserPermissionsRequestSchema) -> list:
        """Синхронизирует права пользователя с переданным набором при редактировании."""
        return self.perm_repo.grant_bulk(user_id, data.permissions)

    def revoke_bulk(
        self, user_id: UUID, data: UserPermissionsRequestSchema
    ) -> int:
        """Массовый отзыв прав"""
        return self.perm_repo.revoke_bulk(user_id, data.permissions)

    def has_access(
        self, user_id: UUID, unit_id: UUID, block: Block, action: Action
    ) -> bool:
        """
        Проверка доступа с учётом наследования по иерархии.
        Алгоритм: проверяем прямое право → поднимаемся к родителю → повторяем.
        """
        # Admin bypass: админ имеет полный доступ без явных записей в user_unit_permissions
        user_role = self.db.query(User.role).filter(User.id == user_id).scalar()
        if user_role == Role.ADMIN:
            return True

        # 1. Прямая проверка
        if self.perm_repo.check_direct_permission(user_id, unit_id, block, action):
            return True

        # 2. Поднимаемся по дереву (наследование)
        current_unit = self.unit_repo.get_by_id(unit_id)
        while current_unit and current_unit.parent_id:
            current_unit = self.unit_repo.get_by_id(current_unit.parent_id)
            if self.perm_repo.check_direct_permission(
                user_id, current_unit.id, block, action
            ):
                return True

        return False

    def get_user_accessible_units(
        self, user_id: UUID, block: Block, action: Action
    ) -> list[UUID]:
        """Получить все unit_id, к которым у пользователя есть доступ (для фильтрации списков)"""
        user_role = self.db.query(User.role).filter(User.id == user_id).scalar()
        if user_role == Role.ADMIN:
            return [unit.id for unit in self.db.query(Unit.id).all()]

        perms = self.perm_repo.get_user_permissions(user_id)
        accessible = set()

        for perm in perms:
            if action == Action.VIEW:
                if perm.action not in [Action.VIEW, Action.MANAGE]:
                    continue
            else:
                if perm.action != action:
                    continue
            if block is None or perm.block in [block, Block.ALL]:
                # Добавляем сам юнит + все дочерние (рекурсивно)
                accessible.add(perm.unit_id)
                accessible.update(self.unit_repo.get_all_descendant_ids(perm.unit_id))

        return list(accessible)
