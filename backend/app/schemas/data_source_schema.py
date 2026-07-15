from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field # type: ignore


class DataSourceCreateRequest(BaseModel):
    """Schema for creating a new data source."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "name": "Fuente CSV de indicadores",
                "description": "Datos para tableros de seguimiento",
                "file_id": 12,
                "updated_at": "2026-04-16",
            }
        },
    )

    name: str = Field(..., min_length=1, description="The data source name")
    description: Optional[str] = Field(None, description="The data source description")
    file_id: int = Field(..., description="The ID of the associated file")
    updated_at: Optional[date] = Field(None, description="The last update date")
