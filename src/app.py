from flask import Flask



import routes.tickets
from utils.exceptions import InternalServerError, AuthenticationFailed
from dotenv import load_dotenv


import routes

load_dotenv()
app = Flask(__name__)

app.register_blueprint(routes.tickets.bp_tickets)


@app.errorhandler(AuthenticationFailed)
def handle_auth_failed(e: AuthenticationFailed):
    return e.to_response()

@app.errorhandler(InternalServerError)
def handle_internal_server_error(e: InternalServerError):
    return e.to_response()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 