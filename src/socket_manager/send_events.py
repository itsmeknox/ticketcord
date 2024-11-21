from utils.schema import Ticket, Message
from flask_socketio import SocketIO

sio: SocketIO = None

def socket_sio_init(socket_client: SocketIO):
    global sio
    sio = socket_client

def send_create_channel_event(ticket: Ticket):
    sio.emit("ticket", ticket.model_dump(exclude={"webhook_url"}), room=ticket.user_id)

def ticket_edit_event(ticket: Ticket):
    sio.emit("edit_ticket", ticket.model_dump(), room=ticket.user_id)

    
def send_message_event(user_id: int, message: Message):
    sio.emit("message", message.model_dump(), room=user_id)

def message_edit_event(user_id: int, message: Message):
    sio.emit("edit_message", message.model_dump(), room=user_id)

def message_delete_event(user_id: int, message: Message):
    sio.emit("delete_message", message.model_dump(), room=user_id)

def ticket_close_event(user_id: int, ticket_id: str):
    sio.emit("ticket_closed", {"id": str(ticket_id)}, room=user_id)