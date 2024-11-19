from flask import request
from pydantic import ValidationError
from typing_extensions import Dict
from utils.schema import TicketUser
from modules.auth import JWT
from utils.exceptions import AuthenticationFailed

from flask_socketio import (
    Namespace, 
    emit, 
    join_room, 
    leave_room
)

import os



jwt = JWT(os.getenv("JWT_SECRET_KEY"))

class SocketHandler(Namespace):
    authenticated_users: Dict[int, TicketUser]  = {}  # Dictionary to track authenticated users by `request.sid`

    def on_authorize(self, data: dict) -> bool:
        """
        Authorizes a user and adds them to their respective room based on their user ID.
        """
        try:
            token = data['token']
            user_data = jwt.decrypt(token)
            user = TicketUser(**user_data)

        except KeyError:
            emit("error", {"message": "Authorization token missing"})
            return False

        except ValidationError as e:
            print("Invalid or expired token")
            emit("error", {"message": f"Invalid token structure: {str(e)}"})
            return False

        except AuthenticationFailed:
            print("Invalid or expired token")
            emit("error", {"message": "Invalid or expired token"})
            return False
        
        
            # Track the user as authenticated
        self.authenticated_users[request.sid] = user
        # Join the user to their specific room (room name based on user ID)

        join_room(user.id)
        emit("authorized", {"message": "User successfully authorized"})
        print(f"User {user.id} authorized and added to their room")
        return True

    def on_connect(self):
        print("User connected:", request.sid)

    def on_disconnect(self):
        """
        Handles user disconnection by removing them from their room and cleaning up state.
        """
        print("User disconnected:", request.sid)

        # Check if the user was authenticated
        user = self.authenticated_users.pop(request.sid, None)
        if user:
            # Leave the user's room (room name based on user ID)
            leave_room(user.id)
            print(f"User {user.id} removed from their room")
        else:
            print("Disconnected user was not authenticated")
