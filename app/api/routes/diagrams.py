from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_active_user
from app.schemas.diagram_schema import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    DiagramAuditResponse,
)
from app.services.diagram_service import DiagramService
from app.services.permission_service import PermissionService
from app.core.enums import Action, Block

router = APIRouter(prefix="/diagrams", tags=["diagrams"])


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_diagram(
    data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Создать новую диаграмму.

    **Block (функциональный блок):**
    - safety: Безопасность
    - quality: Качество
    - production: Производство
    - economy: Затраты
    - culture: Культура
    - all: Все

    Автоматически добавляет:
    - created_by: ID текущего пользователя
    - created_at: Текущая дата/время
    - updated_at: Текущая дата/время
    """
    perm_service = PermissionService(db)
    if not perm_service.has_access(
        current_user.id, data.unit_id, data.block, Action.MANAGE
    ):
        raise HTTPException(
            status_code=403, detail="Нет прав на создание в этом блоке/подразделении"
        )

    service = DiagramService(db)
    return service.create_diagram(data, current_user.id)


@router.get("/", response_model=list[DatasetResponse])
def list_diagrams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block: Block | None = Query(None),
    unit_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Получить список диаграмм с пагинацией."""
    service = DiagramService(db)
    return service.list_diagrams(skip, limit, block, unit_id)


@router.get("/{diagram_id}", response_model=DatasetResponse)
def get_diagram(
    diagram_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Получить одну диаграмму по ID."""
    service = DiagramService(db)
    diagram = service.get_diagram(diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram


@router.patch("/{diagram_id}", response_model=DatasetResponse)
def update_diagram(
    diagram_id: str,
    data: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Обновить существующую диаграмму.

    При обновлении автоматически:
    - Обновляется updated_at на текущее время
    - Создается запись в таблице audit (diagram_audit) с:
      - old_values: предыдущие значения
      - new_values: новые значения
      - updated_by: ID пользователя, сделавшего изменение
    """
    service = DiagramService(db)
    diagram = service.update_diagram(diagram_id, data, current_user.id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram


@router.delete("/{diagram_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagram(
    diagram_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Удалить диаграмму.

    При удалении создается запись в diagram_audit с operation=2 (delete).
    """
    service = DiagramService(db)
    if not service.delete_diagram(diagram_id, current_user.id):
        raise HTTPException(status_code=404, detail="Diagram not found")


@router.get("/{diagram_id}/audit", response_model=list[DiagramAuditResponse])
def get_diagram_audit_logs(
    diagram_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Получить журнал изменений диаграммы (аудит).

    **Operation (тип операции):**
    - 0: Создание (operation=0)
    - 1: Обновление (operation=1)
    - 2: Удаление (operation=2)

    Возвращает записи в обратном порядке (новые первыми).
    """
    service = DiagramService(db)
    diagram = service.get_diagram(diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return service.get_diagram_audit_logs(diagram_id, skip, limit)
