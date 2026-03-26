from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReportCreateRequest(BaseModel):
    """Schema for creating a new report.
    
    Attributes:
        main_title: The main title of the report (required).
        auxiliary_title: The auxiliary title of the report (optional).
        description: The description of the report (optional).
        document_file_id: The ID of the associated file (optional).
        updated_at: The last update timestamp of the report (required).
    """
    model_config = ConfigDict(
        extra='forbid',  
        validate_default=True,
        json_schema_extra={
            "example": {
                "main_title": "Annual Research Report",
                "auxiliary_title": "2025 Data Analysis",
                "description": "Comprehensive analysis of research activities",
                "document_file_id": 42,
                "updated_at": "2026-02-14T21:01:51"
            }
        }
    )
    
    main_title: str = Field(..., min_length=1, description="The main title of the report")
    auxiliary_title: Optional[str] = Field(None, description="The auxiliary title of the report")
    description: Optional[str] = Field(None, description="The description of the report")
    document_file_id: Optional[int] = Field(None, description="The ID of the associated document file")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the report")
    updated_at: datetime = Field(..., description="The last update timestamp of the report")


class ReportUpdateRequest(BaseModel):
    """Schema for updating an existing report.
    
    All fields are optional. Only the provided fields will be updated.
    
    Attributes:
        main_title: The main title of the report (optional).
        auxiliary_title: The auxiliary title of the report (optional).
        description: The description of the report (optional).
        document_file_id: The ID of the associated file (optional).
        updated_at: The last update timestamp of the report (optional).
    """
    model_config = ConfigDict(
        extra='forbid',
        validate_default=True,
        json_schema_extra={
            "example": {
                "main_title": "Updated Report Title",
                "description": "Updated report description",
                "updated_at": "2026-02-15T10:30:00"
            }
        }
    )

    main_title: Optional[str] = Field(None, min_length=1, description="The main title of the report")
    auxiliary_title: Optional[str] = Field(None, description="The auxiliary title of the report")
    description: Optional[str] = Field(None, description="The description of the report")
    document_file_id: Optional[int] = Field(None, description="The ID of the associated document file")
    updated_at: Optional[datetime] = Field(None, description="The last update timestamp of the report")
