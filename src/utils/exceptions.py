import traceback
from flask import jsonify
from pydantic import ValidationError


# Base exception class
class APIException(Exception):
    """Base class for API exceptions."""



    def __init__(self,error_name: str, message: str = "An error occurred", status_code: int = 500, extra: dict=None, error: Exception=None) -> None:
        super().__init__(message)  # Initialize the base Exception class
        self.message = message
        self.status_code = status_code
        self.error_name = error_name



    def get_traceback(self):
        """Capture and format the traceback of the exception."""
        if self.__traceback__:
            return "".join(traceback.format_exception(type(self), self, self.__traceback__))
        else:
            return traceback.format_exc()
            
            
    def to_response(self):
        """Convert the exception to a Flask response."""
        response = {
            "error": self.error_name.capitalize(),
            "message": self.message,
        }
        
        return jsonify(response), self.status_code


class HandledApiException(APIException):
    """Base class for API exceptions that are handled."""
    pass

class CriticalAPIException(APIException):
    """Base class for API exceptions that are critical."""
    pass



# Critical errors
class InternalServerError(CriticalAPIException):
    """Raised when an internal server error occurs."""
    def __init__(self, message: str | None=None, extra: dict=None, error: Exception=None) -> None:
        self.message = message if message else "500 Internal Server Error"
        self.status_code = 500

        super().__init__(error_name="INTERNAL_SERVER_ERROR", message=message, status_code=self.status_code, extra=extra, error=error)



class DatabaseError(CriticalAPIException):
    """Raised when an internal server error occurs."""
    def __init__(self, message: str | None, extra: dict=None, error: Exception=None) -> None:
        self.message = message if message else "500 Internal Server Error"
        self.status_code = 500

        super().__init__(error_name="DATABASE_ERROR", message=message, status_code=self.status_code, extra=extra, error=error)


# User errors
class AuthenticationError(HandledApiException):
    """Raised when the user is not authorised to access the resource."""
    def __init__(self, message: str | None=None, extra: dict=None) -> None:
        self.message = message if message else "401 Unauthorized"
        self.status_code = 401
        
        super().__init__(error_name="UNAUTHORIZED", message=message, status_code=self.status_code, extra=extra)




class NotfoundError(HandledApiException):
    """Raised when the requested resource is not found."""
    def __init__(self, message: str | None=None, extra: dict=None) -> None:
        self.message = message if message else "404 Not Found"
        self.status_code = 404
        
        super().__init__(error_name="NOT_FOUND", message=message, status_code=self.status_code, extra=extra)


class ForbiddenError(HandledApiException):
    """Raised when the user is not authorised to access the resource."""
    def __init__(self, message: str | None=None, extra: dict=None) -> None:
        self.message = message if message else "You do not have permission to do this action."
        self.status_code = 403

        super().__init__(error_name="FORBIDDEN", message=message, status_code=self.status_code, extra=extra)
