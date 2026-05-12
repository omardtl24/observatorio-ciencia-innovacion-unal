from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict # type: ignore


class ReportCreateRequest(BaseModel):
    """Schema for creating a new report.
    
    Attributes:
        title: The main title of the report (required).
        description: The description of the report (optional).
        document_file_id: The ID of the associated file (optional).
        updated_at: The last update timestamp of the report (required).
    """
    model_config = ConfigDict(
        extra='forbid',  
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Annual Research Report",
                "description": "Comprehensive analysis of research activities",
                "document_file_id": 42,
                "updated_at": "2026-02-14T21:01:51"
            }
        }
    )
    
    title: str = Field(..., min_length=1, description="The main title of the report")
    description: Optional[str] = Field(None, description="The description of the report")
    document_file_id: Optional[int] = Field(None, description="The ID of the associated document file")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the report")
    updated_at: datetime = Field(..., description="The last update timestamp of the report")


class ReportUpdateRequest(BaseModel):
    """Schema for updating an existing report.
    
    All fields are optional. Only the provided fields will be updated.
    
    Attributes:
        title: The main title of the report (optional).
        description: The description of the report (optional).
        document_file_id: The ID of the associated file (optional).
        updated_at: The last update timestamp of the report (optional).
    """
    model_config = ConfigDict(
        extra='forbid',
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Updated Report Title",
                "description": "Updated report description",
                "updated_at": "2026-02-15T10:30:00"
            }
        }
    )

    title: Optional[str] = Field(None, min_length=1, description="The main title of the report")
    description: Optional[str] = Field(None, description="The description of the report")
    document_file_id: Optional[int] = Field(None, description="The ID of the associated document file")
    updated_at: Optional[datetime] = Field(None, description="The last update timestamp of the report")
