from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VisorCreateRequest(BaseModel):
    """Schema for creating a new visor.
    
    Attributes:
        name: The name of the visor (required).
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
                "name": "Main Visor",
                "description": "Primary data visualization visor",
                "type": "dashboard",
                "visor_url": "https://example.com/visor",
                "updated_at": "2026-02-14T21:01:51"
            }
        }
    )
    
    name: str = Field(..., min_length=1, description="The name of the visor")
    type: str = Field(..., min_length=1, description="The type of the visor")
    description: str = Field(..., min_length=1, description="The description of the visor")
    visor_url: str = Field(..., min_length=1, description="The URL of the visor")
    updated_at: datetime = Field(..., description="The last update timestamp of the visor")
