from sqlalchemy.orm import Session
from uuid import UUID

from app.models.chart_config_model import ChartConfig
from app.models.diagram_model import Diagram
from app.schemas.chart_schema import ChartCreate, ChartUpdate


class ChartRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ChartCreate) -> ChartConfig:
        chart = ChartConfig(
            dataset_id=data.dataset_id,
            title=data.title,
            chart_type=data.chart_type,
            mapping=data.mapping,
            ui_config=data.ui_config,
            order=data.order or 0,
        )
        self.db.add(chart)
        self.db.flush()
        self.db.commit()
        self.db.refresh(chart)
        return chart

    def get_by_id(self, chart_id: int) -> ChartConfig | None:
        return self.db.query(ChartConfig).filter(ChartConfig.id == chart_id).first()

    def get_all(self, dataset_id: UUID | None = None) -> list[ChartConfig]:
        query = self.db.query(ChartConfig)
        if dataset_id is not None:
            query = query.filter(ChartConfig.dataset_id == dataset_id)
        return query.order_by(ChartConfig.order.asc(), ChartConfig.created_at.asc()).all()

    def update(self, chart: ChartConfig, data: ChartUpdate) -> ChartConfig:
        if data.title is not None:
            chart.title = data.title
        if data.chart_type is not None:
            chart.chart_type = data.chart_type
        if data.dataset_id is not None:
            chart.dataset_id = data.dataset_id
        if data.mapping is not None:
            chart.mapping = data.mapping
        if data.ui_config is not None:
            chart.ui_config = data.ui_config
        if data.order is not None:
            chart.order = data.order

        self.db.flush()
        self.db.commit()
        self.db.refresh(chart)
        return chart

    def delete(self, chart: ChartConfig) -> None:
        self.db.delete(chart)
        self.db.commit()
