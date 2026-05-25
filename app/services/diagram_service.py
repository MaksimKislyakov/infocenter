from sqlalchemy.orm import Session
from uuid import UUID
from app.repositories.diagram_repository import DiagramRepository
from app.schemas.diagram_schema import DatasetCreate, DatasetUpdate, DatasetResponse, DiagramAuditResponse


class DiagramService:
    def __init__(self, db: Session):
        self.repository = DiagramRepository(db)

    def create_diagram(self, data: DatasetCreate, user_id: UUID) -> DatasetResponse:
        diagram = self.repository.create(data, user_id)
        return DatasetResponse.model_validate(diagram)

    def get_diagram(self, diagram_id: str) -> DatasetResponse | None:
        diagram = self.repository.get_by_id(diagram_id)
        if not diagram:
            return None
        return DatasetResponse.model_validate(diagram)

    def list_diagrams(self, skip: int = 0, limit: int = 100) -> list[DatasetResponse]:
        diagrams = self.repository.get_all(skip, limit)
        return [DatasetResponse.model_validate(d) for d in diagrams]

    def update_diagram(self, diagram_id: str, data: DatasetUpdate, user_id: UUID) -> DatasetResponse | None:
        diagram = self.repository.get_by_id(diagram_id)
        if not diagram:
            return None
        updated = self.repository.update(diagram, data, user_id)
        return DatasetResponse.model_validate(updated)

    def delete_diagram(self, diagram_id: str, user_id: UUID) -> bool:
        diagram = self.repository.get_by_id(diagram_id)
        if not diagram:
            return False
        self.repository.delete(diagram, user_id)
        return True

    def get_diagram_audit_logs(self, diagram_id: str, skip: int = 0, limit: int = 100) -> list[DiagramAuditResponse]:
        logs = self.repository.get_audit_logs(diagram_id, skip, limit)
        return [DiagramAuditResponse.model_validate(log) for log in logs]