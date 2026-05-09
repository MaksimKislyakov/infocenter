from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.schemas.diagram_schema import DatasetCreate, DatasetUpdate, DatasetResponse
from app.services.diagram_service import DiagramService

router = APIRouter(prefix="/diagrams", tags=["diagrams"])


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_diagram(
    data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = DiagramService(db)
    return service.create_diagram(data)


@router.get("/", response_model=list[DatasetResponse])
def list_diagrams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = DiagramService(db)
    return service.list_diagrams(skip, limit)


@router.get("/{diagram_id}", response_model=DatasetResponse)
def get_diagram(
    diagram_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = DiagramService(db)
    diagram = service.get_diagram(diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram


@router.put("/{diagram_id}", response_model=DatasetResponse)
def update_diagram(
    diagram_id: str,
    data: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = DiagramService(db)
    diagram = service.update_diagram(diagram_id, data)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram


@router.delete("/{diagram_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagram(
    diagram_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    service = DiagramService(db)
    if not service.delete_diagram(diagram_id):
        raise HTTPException(status_code=404, detail="Diagram not found")