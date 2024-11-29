from flask import Blueprint, request, jsonify
from modules.decorator import ticket_user_required
from database.messages import insert_message, fetch_messages
from database.tickets import fetch_ticket
from utils.helper import send_webhook_message


from utils.exceptions import NotfoundError, ForbiddenError, InternalServerError

from utils.schema import (
    Message, 
    TicketUser, 
    SendMessageRequest, 
    MessageResponse
)

bp_messages = Blueprint('messages', __name__, url_prefix='/api/v1/tickets')



@bp_messages.route('/<ticket_id>/messages', methods=['POST'])
@ticket_user_required
def create_message(ticket_user: TicketUser, ticket_id: str):
    ticket = fetch_ticket(
        ticket_id=ticket_id,
        user_id=ticket_user.id
    )
    if not ticket:
        raise NotfoundError(message="Ticket not found")
    
    if ticket.status != 'ACTIVE':
        raise ForbiddenError(message="This action is not allowed on a closed ticket")

    message_payload = SendMessageRequest.model_validate(request.get_json())
    
    message = Message(
        ticket_id=ticket_id,
        author_id=ticket_user.id,
        author_name=ticket_user.username,
        content=message_payload.content,
        attachments=message_payload.attachments
    )

    success = send_webhook_message(
        url=ticket.webhook_url,
        content=message.content,
        run_as_thread=False
        )
    
    if success is not True:
        raise InternalServerError(message="Failed to send message to deliver your message")

    insert_message(message)

    return jsonify(MessageResponse(**message.model_dump()).model_dump()), 201


@bp_messages.route('/<ticket_id>/messages', methods=['GET'])
@ticket_user_required
def get_messages(ticket_user: TicketUser, ticket_id: str):
    
    ticket = fetch_ticket(
        ticket_id=ticket_id,
        user_id=ticket_user.id
    )
    if ticket is None or ticket.status != 'ACTIVE':
        raise NotfoundError(message="Ticket not found")
    
    messages = fetch_messages(ticket_id)
    return jsonify([MessageResponse(**message.model_dump()).model_dump() for message in messages]), 200
