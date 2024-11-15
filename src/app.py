from flask import Flask

import routes.tickets
app = Flask(__name__)

import routes

app.register_blueprint(routes.tickets.bp_tickets)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 