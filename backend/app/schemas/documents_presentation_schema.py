from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field # type: ignore


class DocumentPresentationCreateRequest(BaseModel):
    """Schema for creating a new document presentation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Presentacion institucional",
                "description": "Documento de presentacion institucional",
                "file_id": 11,
                "updated_at": "2026-03-26",
            }
        },
    )

    title: str = Field(..., min_length=1, description="The main title of the document presentation")
    description: Optional[str] = Field(None, description="The description of the document presentation")
    file_id: Optional[int] = Field(None, description="The ID of the associated file")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the document")
    updated_at: date = Field(..., description="The last update date of the document presentation")


class DocumentPresentationUpdateRequest(BaseModel):
    """Schema for updating an existing document presentation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Presentacion actualizada",
                "description": "Contenido actualizado",
                "updated_at": "2026-03-27",
            }
        },
    )

    title: Optional[str] = Field(None, min_length=1, description="The main title of the document presentation")
    description: Optional[str] = Field(None, description="The description of the document presentation")
    file_id: Optional[int] = Field(None, description="The ID of the associated file")
    updated_at: Optional[date] = Field(None, description="The last update date of the document presentation")
