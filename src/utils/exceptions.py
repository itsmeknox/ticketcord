
from flask import jsonify

class APIException(Exception):
    """Base class for exceptions in this module."""
    
    def to_response(self):
        return jsonify({
            "status": "error",
            "message": self.message
        }), 401


class AuthenticationFailed(APIException):
    """Raised when the user is not authorised to access the resource."""
    def __init__(self, message: str | None=None) -> None:
        self.message = message if message else "401 Unauthorized"
        super().__init__(message)



class InternalServerError(APIException):
    """Raised when an internal server error occurs."""
    def __init__(self, message: str | None) -> None:
        self.message = message if message else "500 Internal Server Error"
        super().__init__(message)


class DatabaseError(APIException):
    """Raised when an internal server error occurs."""
    def __init__(self, message: str | None) -> None:
        self.message = message if message else "500 Internal Server Error"
        super().__init__(message)