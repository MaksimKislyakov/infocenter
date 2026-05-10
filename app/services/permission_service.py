from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.permission_repository import PermissionRepository
from app.repositories.unit_repository import UnitRepository  # создадим ниже
from app.core.enums import Block, Action, OrgLevel
from app.schemas.permission_schema import PermissionGrantSchema, UserPermissionsRequestSchema


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.perm_repo = PermissionRepository(db)
        self.unit_repo = UnitRepository(db)

    def grant_bulk(self, user_id: UUID, data: UserPermissionsRequestSchema) -> list:
        """Массовая выдача прав (при создании/редактировании пользователя)"""
        return [self.perm_repo.grant(user_id, p) for p in data.permissions]

    def revoke_bulk(self, user_id: UUID, permissions: list[PermissionGrantSchema]) -> int:
        """Массовый отзыв прав"""
        return sum(1 for p in permissions if self.perm_repo.revoke(user_id, p))

    def has_access(self, user_id: UUID, unit_id: UUID, block: Block, action: Action) -> bool:
        """
        Проверка доступа с учётом наследования по иерархии.
        Алгоритм: проверяем прямое право → поднимаемся к родителю → повторяем.
        """
        # 1. Прямая проверка
        if self.perm_repo.check_direct_permission(user_id, unit_id, block, action):
            return True
        
        # 2. Поднимаемся по дереву (наследование)
        current_unit = self.unit_repo.get_by_id(unit_id)
        while current_unit and current_unit.parent_id:
            current_unit = self.unit_repo.get_by_id(current_unit.parent_id)
            if self.perm_repo.check_direct_permission(user_id, current_unit.id, block, action):
                return True
        
        return False

    def get_user_accessible_units(self, user_id: UUID, block: Block, action: Action) -> list[UUID]:
        """Получить все unit_id, к которым у пользователя есть доступ (для фильтрации списков)"""
        perms = self.perm_repo.get_user_permissions(user_id)
        accessible = set()
        
        for perm in perms:
            if perm.block in [block, Block.ALL] and perm.action == action:
                # Добавляем сам юнит + все дочерние (рекурсивно)
                accessible.add(perm.unit_id)
                accessible.update(self.unit_repo.get_all_descendant_ids(perm.unit_id))
        
        return list(accessible)