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


IllegalOperation = IllegalOperationError
NotFound = NotFoundError
Forbidden = ForbiddenError
