from flask import Blueprint, request, jsonify
from modules.decorator import ticket_user_required
from database.messages import insert_message, fetch_messages
from database.tickets import fetch_ticket

from utils.schema import (
    Message, 
    TicketUser, 
    SendMessageRequest, 
    MessageResponse
)

bp_messages = Blueprint('messages', __name__, url_prefix='/api/v1/tickets/<int:ticket_id>/messages')



@bp_messages.route('/', methods=['POST'])
@ticket_user_required
def create_message(ticket_user: TicketUser, ticket_id: int):
    ticket = fetch_ticket(
        ticket_id=ticket_id,
        user_id=ticket_user.id
    )
    if not ticket or ticket.status != 'ACTIVE':
        return jsonify({"error": "Ticket not found or not active"}), 404
    
    message_payload = SendMessageRequest.model_validate(request.get_json())
    
    message = Message(
        ticket_id=ticket_id,
        sender_id=ticket_user.id,
        content=message_payload.content,
        attachments=message_payload.attachments
    )
    
    insert_message(message)

    return jsonify(MessageResponse(**message.model_dump()).model_dump()), 201


@bp_messages.route('/', methods=['GET'])
@ticket_user_required
def get_messages(ticket_user: TicketUser, ticket_id: int):
    ticket = fetch_ticket(
        ticket_id=ticket_id,
        user_id=ticket_user.id
    )
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    messages = fetch_messages(ticket_id)
    return jsonify({"messages": [MessageResponse(**message.model_dump()).model_dump() for message in messages]}), 200
