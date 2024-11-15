from flask import Blueprint, request, jsonify

from utils.validator import PostTicketPayload, Ticket, TicketUser
from utils.exceptions import AuthenticationFailed, InternalServerError


from database.tickets import insert_ticket, get_ticket


from modules.auth import JWT
from dotenv import load_dotenv
import os

load_dotenv()

jwt_enc = JWT(encryption_key=os.getenv('SECRET_KEY'))

bp_tickets = Blueprint('tickets', __name__, url_prefix='/tickets')


@bp_tickets.route('/', methods=['POST'])
def create_ticket():
    # Validate the request payload
    ticket_payload = PostTicketPayload.model_validate(request.get_json())

    token = request.headers.get('Authorization', "")
    if not token:
        raise AuthenticationFailed

    # if token is present, decrypt it and if failed raise AuthenticationFailed exception
    user_data = jwt_enc.decrypt(token)
    try:
        ticket_user = TicketUser(id=user_data['user_id'], username=user_data['username'], email=user_data['email'], is_authenticated=user_data['is_authenticated'])
    except KeyError:
        raise InternalServerError("An unexpected error occurred. Field missing in token")

    # Create a ticket object
    ticket_data = Ticket(
        title=ticket_payload.title,
        description=ticket_payload.description,
        user=ticket_user,
        last_seen_message_id=None,
        status="ACTIVE"
    )
    # Need to add the data into database
    insert_ticket(ticket_data)

    # Need to send an socket event
    

    return jsonify(ticket_data.model_dump()), 201

