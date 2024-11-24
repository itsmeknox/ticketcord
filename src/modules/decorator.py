
from functools import wraps
from flask import request
from dotenv import load_dotenv
from utils.exceptions import AuthenticationError, InternalServerError, DatabaseError
from utils.schema import TicketUser

from pydantic import ValidationError
from modules.auth import JWT

import os

load_dotenv()

jwt_enc = JWT(encryption_key=os.getenv('JWT_SECRET_KEY'))

def ticket_user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', "")
        if not token:
            raise AuthenticationError("Authorization header is missing")

        user_data = jwt_enc.decrypt(token)
        try:
            ticket_user = TicketUser(**user_data)
        except ValidationError:
            raise InternalServerError("An unexpected error occurred. Invalid user data in token")

        # Store the user ID safely without modifying headers
        request.user_id = ticket_user.id  # OR g.user_id = ticket_user.id

        return func(ticket_user, *args, **kwargs)
    return wrapper


def database_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            raise DatabaseError(f"An unexpected error occurred")
        
    return wrapper