from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field # type: ignore


class SimulatorCreateRequest(BaseModel):
    """Schema for creating a new simulator."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Simulador de demanda",
                "description": "Simulador de proyeccion de demanda",
                "specs_file_id": 7,
                "updated_at": "2026-03-26",
            }
        },
    )

    title: str = Field(..., min_length=1, description="The main title of the simulator")
    description: Optional[str] = Field(None, description="The description of the simulator")
    specs_file_id: Optional[int] = Field(None, description="The ID of the associated specs file")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the simulator")
    updated_at: date = Field(..., description="The last update date of the simulator")


class SimulatorUpdateRequest(BaseModel):
    """Schema for updating an existing simulator."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Simulador de demanda actualizado",
                "description": "Nueva descripcion",
                "updated_at": "2026-03-27",
            }
        },
    )

    title: Optional[str] = Field(None, min_length=1, description="The main title of the simulator")
    description: Optional[str] = Field(None, description="The description of the simulator")
    specs_file_id: Optional[int] = Field(None, description="The ID of the associated specs file")
    updated_at: Optional[date] = Field(None, description="The last update date of the simulator")
