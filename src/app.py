from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

# monkey.patch_all()

from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
from pydantic import ValidationError
from discord_bot import run_bot


from utils.exceptions import (
    HandledApiException,
    CriticalAPIException
    
)
from utils.helper import send_error_log

from routes.messages import bp_messages
from routes.tickets import bp_tickets, ticket_limiter
from routes.auth import auth_bp


from socket_manager.handler import SocketHandler
from socket_manager.send_events import socket_sio_init
from discord.errors import DiscordException

import json
import os
import traceback

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, cors_allowed_origins="*")

sio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")



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
    socket_sio_init(sio)
    sio.on_namespace(SocketHandler())

def register_blueprints():
    app.register_blueprint(bp_tickets)
    app.register_blueprint(bp_messages)
    app.register_blueprint(auth_bp)



setup_socketio()
register_blueprints()
initialize_limiter()


# ===================== User Error Handlers =====================
@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e: RateLimitExceeded):
    return jsonify({"error": "ratelimit_exceeded", "message": f"You are being ratelimited only {e.description} request are allowed"}), 429


@app.errorhandler(HandledApiException)
def handle_handled_api_exception(e: HandledApiException):
    return e.to_response()



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

    return jsonify({"error": "BAD_REQUEST", "message": "Invalid form of body", "errors": errors}), 400
 

# ===================== Critical Error Handlers =====================
@app.errorhandler(CriticalAPIException)
def handle_critical_api_exception(e: CriticalAPIException):
    # Log the error
    traceback_details = e.get_traceback()
    print(traceback_details)
    send_error_log("Critical API Exception", traceback_details, e)
    return e.to_response()

@app.errorhandler(DiscordException)
def handle_discord_exception(e: DiscordException):
    # Log the error
    trackback_details = traceback.format_exc()
    print("=====================Discord Exception=====================\n")
    print(trackback_details)
    print("\n===========================================================")
    
    send_error_log("Discord Exception", trackback_details, e)
    
    return jsonify({"error": "INTERNAL_SERVER_ERROR", "message": "An error occurred while trying to interact with discord"}), 500


@app.errorhandler
def handle_unhandled_exception(e: Exception):
    traceback_details = traceback.format_exc()
    
    send_error_log("Unhandled Exception", traceback_details, e)
    return jsonify({"message": "An error occurred",}), 500

 


def run_app():
    PORT = os.getenv("WEB_SERVER_PORT")
    if PORT is None:
        raise ValueError("WEB_SERVER_PORT is not set in the environment variables")
    
        
    if os.getenv("SERVER_MODE") == "PRODUCTION":
        print("Running in production mode")
        http_server = WSGIServer(('0.0.0.0', int(PORT)), app, handler_class=WebSocketHandler)
        http_server.serve_forever()
    else:
        print("Running in development mode")
        app.run(host='0.0.0.0', port=PORT, debug=False)


if __name__ == "__main__":
    run_bot()
    run_app()
