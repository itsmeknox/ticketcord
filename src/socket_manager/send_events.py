from utils.schema import TicketResponse, Message
from flask_socketio import SocketIO

sio: SocketIO = None

def socket_sio_init(socket_client: SocketIO):
    global sio
    sio = socket_client


def ticket_close_event(user_id: int, ticket: TicketResponse):
    sio.emit("ticket_closed", ticket.model_dump(exclude={"webhook_url"}), room=user_id)
    
def send_message_event(user_id: int, message: Message):
    sio.emit("message", message.model_dump(), room=user_id)

def message_edit_event(user_id: int, message: Message):
    sio.emit("edit_message", message.model_dump(), room=user_id)

def message_delete_event(user_id: int, message: Message):
    sio.emit("delete_message", message.model_dump(), room=user_id)

