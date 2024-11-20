from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
from pydantic import ValidationError
from waitress import serve
from discord_bot import run_bot


from utils.exceptions import (
    InternalServerError, 
    AuthenticationFailed
)

from routes.messages import bp_messages
from routes.tickets import bp_tickets, ticket_limiter
from socket_manager.handler import SocketHandler
from socket_manager.send_events import socket_sio_init

from discord.errors import DiscordException

import json
import os

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, cors_allowed_origins="*")

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    storage_uri="memory://",
    default_limits=["100 per minute"]
)

def initialize_limiter():
    limiter.init_app(app)
    ticket_limiter.init_app(app)
    
    limiter.limit("10 per minute")(bp_messages)



def setup_socketio() -> SocketIO:
    sio = SocketIO(app, cors_allowed_origins="*")
    socket_sio_init(sio)
    sio.on_namespace(SocketHandler())
    return sio

def register_blueprints():
    app.register_blueprint(bp_tickets)
    app.register_blueprint(bp_messages)

setup_socketio()
register_blueprints()
initialize_limiter()


@app.errorhandler(AuthenticationFailed)
def handle_auth_failed(e: AuthenticationFailed):
    return e.to_response()

@app.errorhandler(InternalServerError)
def handle_internal_server_error(e: InternalServerError):
    return e.to_response()

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e: RateLimitExceeded):
    return jsonify({"error": "ratelimit_exceeded", "message": f"You are being ratelimited only {e.description} request are allowed"}), 429


@app.errorhandler(ValidationError)
def validation_error(e: ValidationError):
    print(e.title)
    errors = []
    
    error_list = json.loads(e.json(include_url=False))

    for error in error_list:
        data = {
            "location": '.'.join(map(str, error['loc'])), 
            "message": error['msg'],
            "type": error['type'],
        }
        if "ctx" in error:
            data['context'] = error['ctx']

        errors.append(data)

    return jsonify({"message": "Invalid form of body", "errors": errors}), 400
 
 
@app.errorhandler(DiscordException)
def handle_discord_exception(e: DiscordException):
    print(e)
    return jsonify({"message": "An error occurred while trying to interact with discord"}), 500


def run_app():
    PORT = os.getenv("WEB_SERVER_PORT")
    if PORT is None:
        raise ValueError("WEB_SERVER_PORT is not set in the environment variables")
    
        
    if os.getenv("MODE") == "PRODUCTION":
        serve(app, host="0.0.0.0", port=PORT)
    else:
        app.run(host='127.0.0.1', port=PORT, debug=False)

if __name__ == '__main__':
    run_bot()
    run_app()
