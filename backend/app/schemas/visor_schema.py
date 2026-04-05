from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VisorCreateRequest(BaseModel):
    """Schema for creating a new visor.
    
    Attributes:
        main_title: The main title of the visor (required).
        auxiliary_title: The auxiliary title of the visor (required).
        type: The type of the visor (required).
        description: The description of the visor (required).
        visor_url: The URL of the visor (required).
        updated_at: The last update timestamp of the visor (required).
    """
    model_config = ConfigDict(
        extra='forbid',  
        validate_default=True,
        json_schema_extra={
            "example": {
                "main_title": "Main Visor title",
                "auxiliary_title": "Auxiliary Visor title",
                "description": "Primary data visualization visor",
                "type": "dashboard",
                "visor_url": "https://example.com/visor",
                "updated_at": "2026-02-14T21:01:51"
            }
        }
    )
    
    main_title: str = Field(..., min_length=1, description="The main title of the visor")
    auxiliary_title: str = Field(..., min_length=1, description="The auxiliary title of the visor")
    type: str = Field(..., min_length=1, description="The type of the visor")
    description: str = Field(..., min_length=1, description="The description of the visor")
    visor_url: str = Field(..., min_length=1, description="The URL of the visor")
    role_ids: List[int] = Field(default_factory=list, description="Role IDs with access to the visor")
    updated_at: datetime = Field(..., description="The last update timestamp of the visor")


class VisorUpdateRequest(BaseModel):
    """Schema for updating an existing visor."""

    model_config = ConfigDict(
        extra='forbid',
        validate_default=True,
        json_schema_extra={
            "example": {
                "main_title": "Main Visor title updated",
                "auxiliary_title": "Auxiliary title updated",
                "description": "Updated visor description",
                "type": "dashboard",
                "visor_url": "https://example.com/visor-updated",
                "updated_at": "2026-02-15T00:00:00"
            }
        }
    )

    main_title: Optional[str] = Field(None, min_length=1, description="The main title of the visor")
    auxiliary_title: Optional[str] = Field(None, min_length=1, description="The auxiliary title of the visor")
    type: Optional[str] = Field(None, min_length=1, description="The type of the visor")
    description: Optional[str] = Field(None, min_length=1, description="The description of the visor")
    visor_url: Optional[str] = Field(None, min_length=1, description="The URL of the visor")
    role_ids: Optional[List[int]] = Field(None, description="Role IDs with access to the visor")
    updated_at: Optional[datetime] = Field(None, description="The last update timestamp of the visor")
