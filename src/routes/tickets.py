from flask import Blueprint, request, jsonify

from utils.validator import (
    PostTicketPayload, 
    Ticket, 
    TicketUser
)
from modules.decorator import ticket_user_required
from discord_bot.app import ticket_manager, bot_run_async_coroutine

from modules.auth import JWT
from dotenv import load_dotenv
import os
import threading

load_dotenv()




create_ticket_lock = threading.Lock()
jwt_enc = JWT(encryption_key=os.getenv('JWT_SECRET_KEY'))

bp_tickets = Blueprint('tickets', __name__, url_prefix='/api/v1/tickets')


@bp_tickets.route('/', methods=['POST'])
@ticket_user_required
def create_ticket(ticket_user: TicketUser):
    # Validate the request payload
    ticket_payload = PostTicketPayload.model_validate(request.get_json())

    # Create a ticket object

    
    channel_id, webhook_url = bot_run_async_coroutine(
        ticket_manager.create_ticket(
        ticket_payload.title,
        description=ticket_payload.description,
        user=ticket_user
    ))

    
    ticket_data = Ticket(
        id=channel_id,
        title=ticket_payload.title,
        description=ticket_payload.description,
        user=ticket_user,
        last_seen_message_id=None,
        webhook_url=webhook_url,
        status="ACTIVE"
    )



    return jsonify(ticket_data.model_dump(exclude="webhook_url")), 201