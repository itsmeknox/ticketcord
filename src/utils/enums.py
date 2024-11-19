from enum import Enum

# Enums for Role and Status
class UserRole(str, Enum):
    TEMP_USER = "TEMP_USER"
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"

class TicketStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DELETED = "DELETED"
