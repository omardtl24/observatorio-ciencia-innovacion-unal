from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SimulatorCreateRequest(BaseModel):
    """Schema for creating a new simulator."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "main_title": "Simulador de demanda",
                "auxiliary_title": "Escenario base 2026",
                "description": "Simulador de proyeccion de demanda",
                "specs_file_id": 7,
                "updated_at": "2026-03-26T10:00:00",
            }
        },
    )

    main_title: str = Field(..., min_length=1, description="The main title of the simulator")
    auxiliary_title: Optional[str] = Field(None, description="The auxiliary title of the simulator")
    description: Optional[str] = Field(None, description="The description of the simulator")
    specs_file_id: Optional[int] = Field(None, description="The ID of the associated specs file")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the simulator")
    updated_at: datetime = Field(..., description="The last update timestamp of the simulator")


class SimulatorUpdateRequest(BaseModel):
    """Schema for updating an existing simulator."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "main_title": "Simulador de demanda actualizado",
                "description": "Nueva descripcion",
                "updated_at": "2026-03-27T08:30:00",
            }
        },
    )

    main_title: Optional[str] = Field(None, min_length=1, description="The main title of the simulator")
    auxiliary_title: Optional[str] = Field(None, description="The auxiliary title of the simulator")
    description: Optional[str] = Field(None, description="The description of the simulator")
    specs_file_id: Optional[int] = Field(None, description="The ID of the associated specs file")
    updated_at: Optional[datetime] = Field(None, description="The last update timestamp of the simulator")
