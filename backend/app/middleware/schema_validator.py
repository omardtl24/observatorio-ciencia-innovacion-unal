from functools import wraps
from flask import request
from app.api.utils.validate_schema import validate_schema
from app.domain.exceptions import SchemaValidationError


def schema_validator(schema_class):
    """Decorator middleware to validate request JSON payload against a Pydantic schema.
    
    Args:
        schema_class: A Pydantic model class to validate against.
    
    Returns:
        function: A decorator that validates the request payload.
    
    Example:
        @app.route('/user', methods=['POST'])
        @schema_validator(UserCreateSchema)
        def create_user():
            return jsonify({"message": "User created"}), 201
    
    Notes:
        - Expects a JSON request body
        - Raises SchemaValidationError if validation fails (propagates to global error handler)
        - Rejects any fields not defined in the schema
        - Passes validated data to route handler via 'request.validated_data'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get JSON data from request
            data = request.get_json()
            
            if data is None:
                raise SchemaValidationError("El cuerpo de la solicitud debe estar en formato JSON")
            
            # Validate data using the util function (raises SchemaValidationError on failure)
            # This exception will be caught by the global error handler in app/__init__.py
            validated_data = validate_schema(data, schema_class)
            
            # Store validated data in the request context
            request.validated_data = validated_data
            
            # Call the original route handler
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

