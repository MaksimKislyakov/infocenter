from sqlalchemy.orm import Session

from app.repositories.chart_repository import ChartRepository
from app.schemas.chart_schema import ChartCreate, ChartUpdate, ChartResponse


class ChartService:
    def __init__(self, db: Session):
        self.repository = ChartRepository(db)

    def create_chart(self, data: ChartCreate) -> ChartResponse:
        chart = self.repository.create(data)
        return ChartResponse.model_validate(chart)

    def get_chart(self, chart_id: int) -> ChartResponse | None:
        chart = self.repository.get_by_id(chart_id)
        if not chart:
            return None
        return ChartResponse.model_validate(chart)

    def list_charts(self, dataset_id: str | None = None) -> list[ChartResponse]:
        charts = self.repository.get_all(dataset_id)
        return [ChartResponse.model_validate(chart) for chart in charts]

    def update_chart(self, chart_id: int, data: ChartUpdate) -> ChartResponse | None:
        chart = self.repository.get_by_id(chart_id)
        if not chart:
            return None
        updated = self.repository.update(chart, data)
        return ChartResponse.model_validate(updated)

    def delete_chart(self, chart_id: int) -> bool:
        chart = self.repository.get_by_id(chart_id)
        if not chart:
            return False
        self.repository.delete(chart)
        return True
