from flask import Blueprint, request, jsonify
from flask_limiter import Limiter

from typing_extensions import List


from modules.decorator import ticket_user_required
from modules.auth import JWT

from utils.enums import TicketStatus
from utils.helper import rate_limit_handler
from utils.schema import (
    CreateTicketRequest, 
    Ticket, 
    TicketUser,
    TicketResponse
)

from discord.errors import DiscordException

from discord_bot.app import (
    ticket_manager, 
    bot_run_async_coroutine
)

from database.tickets import (
    insert_ticket, 
    fetch_ticket, 
    fetch_user_tickets
)

import os
import threading



   

ticket_limiter = Limiter(
    rate_limit_handler,
    storage_uri="memory://"
) 
create_ticket_lock = threading.Lock()
jwt_enc = JWT(encryption_key=os.getenv('JWT_SECRET_KEY'))

bp_tickets = Blueprint('tickets', __name__, url_prefix='/api/v1/tickets')




@bp_tickets.route('', methods=['POST'])
@ticket_limiter.limit("3 per minute")
@ticket_user_required
def create_ticket(ticket_user: TicketUser):
    # Validate the request payload
    ticket_payload = CreateTicketRequest.model_validate(request.get_json())

    try:
        channel_id, webhook_url = bot_run_async_coroutine(
        ticket_manager.create_ticket(
        ticket_payload.topic,
        description=ticket_payload.description,
        user=ticket_user
    ))
    except DiscordException as e:
        return jsonify({"error": str(e)}), 500  
    
    print(channel_id)
    
    ticket_data = Ticket(
        id=str(channel_id),
        user_id=ticket_user.id,
        user_email=ticket_user.email,
        username=ticket_user.username,
        channel_id=channel_id,
        user_role=ticket_user.role,
        topic=ticket_payload.topic,
        description=ticket_payload.description,
        webhook_url=webhook_url
    )


    insert_ticket(ticket_data)
    data = TicketResponse(**ticket_data.model_dump()).model_dump()

    print(data)
    return jsonify(data), 201


@bp_tickets.route('/<int:ticket_id>', methods=['GET'])
@ticket_user_required
def get_ticket(ticket_user: TicketUser, ticket_id: int):
    
    ticket_data = fetch_ticket(
        ticket_id=ticket_id,
        user_id=ticket_user.id
    )
    if not ticket_data:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify(TicketResponse(**ticket_data.model_dump()).model_dump()), 200



@bp_tickets.route('', methods=['GET'])
@ticket_user_required
def get_tickets(ticket_user: TicketUser):
    tickets: List[Ticket] = fetch_user_tickets(ticket_user.id, status=[TicketStatus.ACTIVE])

    ticket_list = [TicketResponse(**ticket.model_dump()).model_dump() for ticket in tickets]
    
    return jsonify(ticket_list), 200

