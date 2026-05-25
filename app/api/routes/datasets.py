from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.services.diagram_service import DiagramService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("/{dataset_id}")
def get_dataset_rows(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Получить плоские данные для диаграммы (tidy data)."""
    service = DiagramService(db)
    rows = service.get_dataset_rows(dataset_id)
    if rows is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return rows
