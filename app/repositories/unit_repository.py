from sqlalchemy.orm import Session
from uuid import UUID

from app.models.unit_model import Unit


class UnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, unit_id: UUID) -> Unit | None:
        return self.db.query(Unit).filter(Unit.id == unit_id).first()

    def get_all_descendant_ids(self, unit_id: UUID) -> set[UUID]:
        """Рекурсивно получить все ID дочерних подразделений"""
        descendants = set()
        children = self.db.query(Unit).filter(Unit.parent_id == unit_id).all()
        
        for child in children:
            descendants.add(child.id)
            descendants.update(self.get_all_descendant_ids(child.id))
        
        return descendants

    def get_tree(self, root_id: UUID | None = None) -> list[dict]:
        """Получить дерево подразделений (для админки)"""
        query = self.db.query(Unit)
        if root_id:
            # Упрощённо: получаем всех, фильтрация на клиенте или доработать рекурсию
            pass
        units = query.all()
        
        units_map = {u.id: {"id": u.id, "name": u.name, "level": u.level_type, "children": []} for u in units}
        root_nodes = []
        
        for u in units:
            if u.parent_id and u.parent_id in units_map:
                units_map[u.parent_id]["children"].append(units_map[u.id])
            elif not u.parent_id:
                root_nodes.append(units_map[u.id])
        
        return root_nodes