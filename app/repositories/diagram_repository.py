from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.diagram_model import Diagram
from app.models.diagram_audit_model import DiagramAudit
from app.schemas.diagram_schema import DatasetCreate, DatasetUpdate


class DiagramRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DatasetCreate, user_id: UUID) -> Diagram:
        diagram = Diagram(
            block=data.block,
            unit_id=data.unit_id,
            order=(
                data.order
                if data.order is not None
                else self._next_order(data.block, data.unit_id)
            ),
            columns=[c.model_dump() for c in data.columns],
            rows=data.rows,
            created_by=user_id,
        )
        self.db.add(diagram)
        self.db.flush()

        # Create audit log for creation
        audit_log = DiagramAudit(
            diagram_id=diagram.id,
            updated_by=user_id,
            operation=0,  # 0 = create
            new_values={
                "block": str(data.block.value),
                "unit_id": str(data.unit_id),
                "order": diagram.order,
                "columns": [c.model_dump() for c in data.columns],
                "rows": data.rows,
            },
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(diagram)
        return diagram

    def get_by_id(self, diagram_id: str) -> Diagram | None:
        return self.db.query(Diagram).filter(Diagram.id == diagram_id).first()

    def get_all(
        self, skip: int = 0, limit: int = 100, block=None, unit_id=None
    ) -> list[Diagram]:
        query = self.db.query(Diagram)
        if block is not None:
            query = query.filter(Diagram.block == block)
        if unit_id is not None:
            query = query.filter(Diagram.unit_id == unit_id)
        return (
            query.order_by(Diagram.order.asc(), Diagram.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _next_order(self, block, unit_id):
        max_order = (
            self.db.query(func.max(Diagram.order))
            .filter(
                Diagram.block == block,
                Diagram.unit_id == unit_id,
            )
            .scalar()
        )
        return (max_order or 0) + 1

    def update(self, diagram: Diagram, data: DatasetUpdate, user_id: UUID) -> Diagram:
        # Store old values for audit
        old_values = {
            "block": str(diagram.block.value),
            "unit_id": str(diagram.unit_id),
            "order": diagram.order,
            "columns": diagram.columns,
            "rows": diagram.rows,
        }

        if data.block is not None:
            diagram.block = data.block
        if data.unit_id is not None:
            diagram.unit_id = data.unit_id
        if data.order is not None:
            diagram.order = data.order
        if data.columns is not None:
            diagram.columns = [c.model_dump() for c in data.columns]
        if data.rows is not None:
            diagram.rows = data.rows

        new_values = {
            "block": str(diagram.block.value),
            "unit_id": str(diagram.unit_id),
            "order": diagram.order,
            "columns": diagram.columns,
            "rows": diagram.rows,
        }

        self.db.flush()

        # Create audit log for update
        audit_log = DiagramAudit(
            diagram_id=diagram.id,
            updated_by=user_id,
            operation=1,  # 1 = update
            old_values=old_values,
            new_values=new_values,
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(diagram)
        return diagram

    def delete(self, diagram: Diagram, user_id: UUID) -> None:
        # Create audit log for deletion
        audit_log = DiagramAudit(
            diagram_id=diagram.id,
            updated_by=user_id,
            operation=2,  # 2 = delete
            old_values={
                "block": str(diagram.block.value),
                "unit_id": str(diagram.unit_id),
                "columns": diagram.columns,
                "rows": diagram.rows,
            },
        )
        self.db.add(audit_log)
        self.db.delete(diagram)
        self.db.commit()

    def get_audit_logs(
        self, diagram_id: str, skip: int = 0, limit: int = 100
    ) -> list[DiagramAudit]:
        return (
            self.db.query(DiagramAudit)
            .filter(DiagramAudit.diagram_id == diagram_id)
            .order_by(DiagramAudit.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
