from werkzeug.exceptions import HTTPException # type: ignore


class DomainError(HTTPException):
    """Base class for all domain exceptions."""

    code = 400
    error_code = "domain_error"
    default_message = "Ocurrió un error en la operación solicitada"

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
    default_message = "La operación solicitada no es válida"


class NotFoundError(DomainError):
    code = 404
    error_code = "not_found"
    default_message = "No se encontró el recurso solicitado"


class ForbiddenError(DomainError):
    code = 403
    error_code = "forbidden"
    default_message = "No tienes permiso para realizar esta operación"

class UnauthorizedError(DomainError):
    code = 401
    error_code = "unauthorized"
    default_message = "No estás autorizado para realizar esta operación"


class SchemaValidationError(DomainError):
    code = 400
    error_code = "schema_validation_error"
    default_message = "Los datos enviados no son válidos"


class DatabaseConnectionError(DomainError):
    code = 503
    error_code = "database_connection_error"
    default_message = "El servicio de base de datos no está disponible. Intenta nuevamente más tarde."


IllegalOperation = IllegalOperationError
NotFound = NotFoundError
Forbidden = ForbiddenError
Unauthorized = UnauthorizedError
SchemaValidation = SchemaValidationError
DatabaseConnection = DatabaseConnectionError
