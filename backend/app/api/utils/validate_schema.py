"""Schema validation utility for request payloads."""
from pydantic import ValidationError, BaseModel
from app.domain.exceptions import SchemaValidationError


def validate_schema(data: dict, schema_class: BaseModel):
    """Validate data against a Pydantic schema.
    
    Args:
        data (dict): The data to validate.
        schema_class (BaseModel): A Pydantic model class to validate against.
    
    Returns:
        object: The validated model instance if validation passes.
    
    Raises:
        SchemaValidationError: If validation fails with details about the errors.
    
    Example:
        try:
            validated_model = validate_schema(request_data, VisorCreateRequest)
        except SchemaValidationError as e:
            return jsonify(e.to_dict()), 400
    """
    try:
        validated_data = schema_class(**data)
        return validated_data
    
    except ValidationError as e:
        # Format Pydantic validation errors
        errors = {}
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            errors[field] = error["msg"]
        
        raise SchemaValidationError("Request validation failed", details=errors)
    
    except Exception as e:
        raise SchemaValidationError(str(e))
