from flask import Blueprint, request, jsonify
from database.messages import insert_message
from modules.decorator import ticket_user_required
from utils.validator import Message, TicketUser, PostMessagePayload, MessageUser
bp_messages = Blueprint('messages', __name__, url_prefix='/api/v1/tickets/<int:ticket_id>/messages')



@bp_messages.route('/', methods=['POST'])
@ticket_user_required
def create_message(ticket_user: TicketUser, ticket_id: int):
    message_payload = PostMessagePayload.model_validate(request.get_json())
    
    message = Message(
        content=message_payload.content,
        user=MessageUser(
            id=ticket_user.id,
            username=ticket_user.username
        )
    )
    
    try:
        insert_message(ticket_id, message)
    except ValueError as e:
        return jsonify({"error": "Ticket Not found"}), 404
    
    return jsonify({}), 204
