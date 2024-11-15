from flask import Blueprint, request, jsonify

from utils.validator import PostTicketPayload, Ticket, TicketUser
from utils.exceptions import AuthenticationFailed



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

    if ticket_payload.user is None:
        token = request.headers.get('Authorization', "")
        if not token:
            raise AuthenticationFailed
        
        # if token is present, decrypt it and if failed raise AuthenticationFailed exception
        user_data = jwt_enc.decrypt(token)
        ticket_user = TicketUser(username=user_data['username'], email=user_data['email'], is_authenticated=True)

    else:
        ticket_user = TicketUser(username=ticket_payload.user.username, email=ticket_payload.user.email, is_authenticated=False)


    ticket_data = Ticket(
        title=ticket_payload.title,
        description=ticket_payload.description,
        user=ticket_user,
        last_seen_message_id=None,
        status="ACTIVE"
    )

    # Need to add the data into database

    # Need to send an socket event

    return jsonify(ticket_data.model_dump()), 201
