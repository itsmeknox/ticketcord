from flask import Flask



import routes.messages
import routes.tickets
from utils.exceptions import InternalServerError, AuthenticationFailed
from dotenv import load_dotenv

from waitress import serve
from discord_bot import run_bot


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


def run_app():
    PORT = os.getenv("WEB_SERVER_PORT")
    if PORT is None:
        raise ValueError("WEB_SERVER_PORT is not set in the environment variables")
    
        
    if os.getenv("MODE") == "PRODUCTION":
        serve(app, host="0.0.0.0", port=PORT)
    else:
        app.run(host='127.0.0.1', port=PORT, debug=True)


if __name__ == '__main__':
    run_bot()
    run_app()
 