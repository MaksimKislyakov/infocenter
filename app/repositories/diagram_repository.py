from sqlalchemy.orm import Session
from app.models.diagram_model import Diagram
from app.schemas.diagram_schema import DatasetCreate, DatasetUpdate


class DiagramRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DatasetCreate) -> Diagram:
        diagram = Diagram(
            diagramm_id=data.diagramm_id,
            columns=[c.model_dump() for c in data.columns],
            rows=data.rows,
        )
        self.db.add(diagram)
        self.db.commit()
        self.db.refresh(diagram)
        return diagram

    def get_by_id(self, diagram_id: str) -> Diagram | None:
        return self.db.query(Diagram).filter(Diagram.diagramm_id == diagram_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Diagram]:
        return self.db.query(Diagram).offset(skip).limit(limit).all()

    def update(self, diagram: Diagram, data: DatasetUpdate) -> Diagram:
        if data.diagramm_id:
            diagram.diagramm_id = data.diagramm_id
        diagram.columns = [c.model_dump() for c in data.columns]
        diagram.rows = data.rows
        self.db.commit()
        self.db.refresh(diagram)
        return diagram

    def delete(self, diagram: Diagram) -> None:
        self.db.delete(diagram)
        self.db.commit()