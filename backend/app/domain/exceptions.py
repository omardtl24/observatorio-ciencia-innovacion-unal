from werkzeug.exceptions import HTTPException


class DomainError(HTTPException):
    """Base class for all domain exceptions."""

    code = 400
    error_code = "domain_error"
    default_message = "A domain error occurred"

    def __init__(self, message: str | None = None, *, details=None):
        self.message = message or self.default_message
        self.details = details
        super().__init__(description=self.message)

    def to_dict(self):
        return {
            "code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class IllegalOperationError(DomainError):
    code = 400
    error_code = "illegal_operation"
    default_message = "Illegal operation"


class NotFoundError(DomainError):
    code = 404
    error_code = "not_found"
    default_message = "Resource not found"


class ForbiddenError(DomainError):
    code = 403
    error_code = "forbidden"
    default_message = "Operation not allowed"

class UnauthorizedError(DomainError):
    code = 401
    error_code = "unauthorized"
    default_message = "Operation not authorized"


class SchemaValidationError(DomainError):
    code = 400
    error_code = "schema_validation_error"
    default_message = "Request validation failed"


class DatabaseConnectionError(DomainError):
    code = 503
    error_code = "database_connection_error"
    default_message = "Database service unavailable. Please try again later."


IllegalOperation = IllegalOperationError
NotFound = NotFoundError
Forbidden = ForbiddenError
Unauthorized = UnauthorizedError
SchemaValidation = SchemaValidationError
DatabaseConnection = DatabaseConnectionError
