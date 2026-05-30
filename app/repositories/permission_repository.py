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
        """Синхронизирует права пользователя с переданным набором.

        Удаляет лишние права, добавляет новые и оставляет существующие.
        """
        requested_keys = {
            (perm.unit_id, perm.block, perm.action) for perm in permissions
        }

        existing_perms = (
            self.db.query(UserUnitPermission)
            .filter(UserUnitPermission.user_id == user_id)
            .all()
        )
        existing_map = {
            (perm.unit_id, perm.block, perm.action): perm
            for perm in existing_perms
        }

        granted: list[UserUnitPermission] = []
        perms_to_add: list[UserUnitPermission] = []

        # Оставляем существующие права и создаём недостающие
        for perm in permissions:
            key = (perm.unit_id, perm.block, perm.action)
            if key in existing_map:
                granted.append(existing_map[key])
            else:
                perms_to_add.append(
                    UserUnitPermission(
                        user_id=user_id,
                        unit_id=perm.unit_id,
                        block=perm.block,
                        action=perm.action,
                    )
                )

        # Удаляем права, которые больше не присутствуют в запросе
        to_delete = [
            perm for key, perm in existing_map.items() if key not in requested_keys
        ]

        if to_delete or perms_to_add:
            for perm in to_delete:
                self.db.delete(perm)
            if perms_to_add:
                self.db.add_all(perms_to_add)
            self.db.commit()
            for perm in perms_to_add:
                self.db.refresh(perm)
            granted.extend(perms_to_add)

        return granted

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
        return (
            self.db.query(UserUnitPermission.id)
            .filter(
                UserUnitPermission.user_id == user_id,
                UserUnitPermission.unit_id == unit_id,
                UserUnitPermission.block.in_([block, Block.ALL]),
                UserUnitPermission.action == action,
            )
            .first()
            is not None
        )
