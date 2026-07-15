from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict # type: ignore


class VisorCreateRequest(BaseModel):
    """Schema for creating a new visor.
    
    Attributes:
        title: The main title of the visor (required).
        description: The description of the visor (required).
        updated_at: The last update date of the visor (required).
    """
    model_config = ConfigDict(
        extra='forbid',  
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Main Visor title",
                "description": "Primary data visualization visor",
                "updated_at": "2026-02-14"
            }
        }
    )
    
    title: str = Field(..., min_length=1, description="The main title of the visor")
    description: str = Field(..., min_length=1, description="The description of the visor")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the visor")
    updated_at: date = Field(..., description="The last update date of the visor")


class VisorUpdateRequest(BaseModel):
    """Schema for updating an existing visor."""

    model_config = ConfigDict(
        extra='forbid',
        validate_default=True,
        json_schema_extra={
            "example": {
                "title": "Main Visor title updated",
                "description": "Updated visor description",
                "updated_at": "2026-02-15"
            }
        }
    )

    title: Optional[str] = Field(None, min_length=1, description="The main title of the visor")
    description: Optional[str] = Field(None, min_length=1, description="The description of the visor")
    role_ids: Optional[List[int]] = Field(None, description="Role IDs with access to the visor")
    updated_at: Optional[date] = Field(None, description="The last update date of the visor")
