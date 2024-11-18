
from functools import wraps
from flask import request
from dotenv import load_dotenv
from utils.exceptions import AuthenticationFailed, InternalServerError
from utils.validator import TicketUser

from modules.auth import JWT

import os

load_dotenv()

jwt_enc = JWT(encryption_key=os.getenv('JWT_SECRET_KEY'))


def ticket_user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', "")
        if not token:
            raise AuthenticationFailed

        user_data = jwt_enc.decrypt(token)
        print(user_data)
        try:
            ticket_user = TicketUser(id=user_data['id'], username=user_data['username'], email=user_data['email'], is_authenticated=user_data['is_authenticated'])
        except KeyError:
            raise InternalServerError("An unexpected error occurred. Fields are missing in token")

        return func(ticket_user, *args, **kwargs)
    return wrapper