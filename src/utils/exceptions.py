

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class AuthenticationFailed(Error):
    """Raised when the user is not authorised to access the resource."""
    def __init__(self, message: str | None) -> None:
        self.message = message
        super().__init__(message)



class InternalServerError(Error):
    """Raised when an internal server error occurs."""
    def __init__(self, message: str | None) -> None:
        self.message = message
        super().__init__(message)
        
