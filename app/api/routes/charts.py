from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_active_user
from app.schemas.chart_schema import ChartCreate, ChartResponse, ChartUpdate
from app.services.chart_service import ChartService
from app.services.permission_service import PermissionService
from app.repositories.diagram_repository import DiagramRepository
from app.core.enums import Action

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/", response_model=list[ChartResponse])
def list_charts(
    diagram_id: UUID | None = Query(None, alias="diagramId"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Получить конфиги графиков. Можно фильтровать по diagramId."""
    service = ChartService(db)
    return service.list_charts(diagram_id)


@router.post("/", response_model=ChartResponse, status_code=status.HTTP_201_CREATED)
def create_chart(
    data: ChartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Создать конфигурацию графика для диаграммы."""
    # Проверяем права на unit/block диаграммы
    diagram_repo = DiagramRepository(db)
    diagram = diagram_repo.get_by_id(data.diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    perm_service = PermissionService(db)
    if not perm_service.has_access(current_user.id, diagram.unit_id, diagram.block, Action.MANAGE):
        raise HTTPException(status_code=403, detail="Нет прав на создание конфигурации графика для этой диаграммы")

    service = ChartService(db)
    return service.create_chart(data)


@router.put("/{chart_id}", response_model=ChartResponse)
def update_chart(
    chart_id: int,
    data: ChartUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Обновить конфигурацию графика."""
    # Проверяем права на unit/block диаграммы
    service = ChartService(db)
    chart = service.get_chart(chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    diagram_repo = DiagramRepository(db)
    diagram = diagram_repo.get_by_id(chart.diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    perm_service = PermissionService(db)
    if not perm_service.has_access(current_user.id, diagram.unit_id, diagram.block, Action.MANAGE):
        raise HTTPException(status_code=403, detail="Нет прав на обновление конфигурации графика для этой диаграммы")

    chart = service.update_chart(chart_id, data)
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    return chart


@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chart(
    chart_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = ChartService(db)
    chart = service.get_chart(chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    diagram_repo = DiagramRepository(db)
    diagram = diagram_repo.get_by_id(chart.diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    perm_service = PermissionService(db)
    if not perm_service.has_access(current_user.id, diagram.unit_id, diagram.block, Action.MANAGE):
        raise HTTPException(status_code=403, detail="Нет прав на удаление конфигурации графика для этой диаграммы")
    if not service.delete_chart(chart_id):
        raise HTTPException(status_code=404, detail="Chart not found")
