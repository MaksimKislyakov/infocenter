from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_active_user
from app.schemas.chart_schema import ChartCreate, ChartResponse, ChartUpdate
from app.services.chart_service import ChartService

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/", response_model=list[ChartResponse])
def list_charts(
    dataset_id: UUID | None = Query(None, alias="datasetId"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Получить конфиги графиков. Можно фильтровать по datasetId."""
    service = ChartService(db)
    return service.list_charts(dataset_id)


@router.post("/", response_model=ChartResponse, status_code=status.HTTP_201_CREATED)
def create_chart(
    data: ChartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Создать конфигурацию графика для диаграммы."""
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
    service = ChartService(db)
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
    if not service.delete_chart(chart_id):
        raise HTTPException(status_code=404, detail="Chart not found")
