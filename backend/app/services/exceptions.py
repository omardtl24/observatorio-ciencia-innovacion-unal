class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""
    pass

class IllegalOperationError(Exception):
    """Raised when a requested action is invalid (e.g., deleting data with dependencies)."""
    pass