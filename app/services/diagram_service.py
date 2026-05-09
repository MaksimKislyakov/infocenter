from sqlalchemy.orm import Session
from app.repositories.diagram_repository import DiagramRepository
from app.schemas.diagram_schema import DatasetCreate, DatasetUpdate, DatasetResponse


class DiagramService:
    def __init__(self, db: Session):
        self.repository = DiagramRepository(db)

    def create_diagram(self, data: DatasetCreate) -> DatasetResponse:
        diagram = self.repository.create(data)
        return DatasetResponse.model_validate(diagram)

    def get_diagram(self, diagram_id: str) -> DatasetResponse | None:
        diagram = self.repository.get_by_id(diagram_id)
        if not diagram:
            return None
        return DatasetResponse.model_validate(diagram)

    def list_diagrams(self, skip: int = 0, limit: int = 100) -> list[DatasetResponse]:
        diagrams = self.repository.get_all(skip, limit)
        return [DatasetResponse.model_validate(d) for d in diagrams]

    def update_diagram(self, diagram_id: str, data: DatasetUpdate) -> DatasetResponse | None:
        diagram = self.repository.get_by_id(diagram_id)
        if not diagram:
            return None
        updated = self.repository.update(diagram, data)
        return DatasetResponse.model_validate(updated)

    def delete_diagram(self, diagram_id: str) -> bool:
        diagram = self.repository.get_by_id(diagram_id)
        if not diagram:
            return False
        self.repository.delete(diagram)
        return True