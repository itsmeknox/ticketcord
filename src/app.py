from flask import Flask, jsonify



import routes.messages
import routes.tickets
from utils.exceptions import InternalServerError, AuthenticationFailed
from dotenv import load_dotenv

from pydantic import ValidationError
from waitress import serve
from discord_bot import run_bot

import json
import routes
import os


load_dotenv()
app = Flask(__name__)

app.register_blueprint(routes.tickets.bp_tickets)
app.register_blueprint(routes.messages.bp_messages)


@app.errorhandler(AuthenticationFailed)
def handle_auth_failed(e: AuthenticationFailed):
    return e.to_response()

@app.errorhandler(InternalServerError)
def handle_internal_server_error(e: InternalServerError):
    return e.to_response()

@app.errorhandler(ValidationError)
def validation_error(e: ValidationError):
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
 