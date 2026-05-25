from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, require_admin
from app.models.unit_model import Unit
from app.core.enums import OrgLevel

router = APIRouter(prefix="/units", tags=["units"])


@router.post("/", status_code=201)
def create_unit(
    name: str,
    level_type: OrgLevel,
    parent_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Создать новое подразделение (только админ).
    
    **OrgLevel (уровень организационной иерархии):**
    - enterprise: Предприятие (верхний уровень, без parent_id)
    - shop: Цех (средний уровень, parent_id = предприятие)
    - area: Участок (нижний уровень, parent_id = цех)
    
    **parent_id:** ID родительского подразделения (nullable для enterprise)
    """
    unit = Unit(name=name, level_type=level_type, parent_id=parent_id)
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.get("/")
def list_units(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Получить все подразделения."""
    return db.query(Unit).all()


@router.get("/tree")
def get_units_tree(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Получить иерархическое дерево подразделений."""
    units = db.query(Unit).all()
    units_map = {u.id: {"id": u.id, "name": u.name, "level": u.level_type, "children": []} for u in units}
    roots = []
    for u in units:
        if u.parent_id and u.parent_id in units_map:
            units_map[u.parent_id]["children"].append(units_map[u.id])
        elif not u.parent_id:
            roots.append(units_map[u.id])
    return roots