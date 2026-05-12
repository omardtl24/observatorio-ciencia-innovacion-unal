from pydantic import BaseModel, ConfigDict, Field # type: ignore


class PermissionRefreshTokenUpdateRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        json_schema_extra={
            "example": {
                "refresh_token": "1//new_refresh_token_from_reauth",
            }
        },
    )

    refresh_token: str = Field(..., min_length=1, description="Nuevo refresh token")