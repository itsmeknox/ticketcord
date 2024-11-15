from flask import Blueprint, request, jsonify

from utils.validator import PostTicketPayload, Ticket, TicketUser
from utils.exceptions import AuthenticationFailed, InternalServerError


from database.tickets import insert_ticket, get_ticket
from modules.decorator import ticket_user_required
from socket_manager.send_events import send_create_channel_event


from modules.auth import JWT
from dotenv import load_dotenv
import os

load_dotenv()

jwt_enc = JWT(encryption_key=os.getenv('SECRET_KEY'))

bp_tickets = Blueprint('tickets', __name__, url_prefix='/api/v1/tickets')


@bp_tickets.route('/', methods=['POST'])
@ticket_user_required
def create_ticket(ticket_user: TicketUser):
    # Validate the request payload
    ticket_payload = PostTicketPayload.model_validate(request.get_json())

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
    send_create_channel_event(ticket_data)

    return jsonify(ticket_data.model_dump()), 201