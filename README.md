# Ticket Support System Backend

### Project by Kamendra Gupta

## Overview

This backend system provides a ticket support system with various endpoints and socket events to manage tickets and messages.


# Project Details

### Why We Implemented JWT Tokens in the Ticket System

- ### **Reason for Using JWT Tokens**
The primary reason for implementing JWT tokens in our app is to **enable flexible user authentication** by delegating the responsibility to external trusted backends. This approach allows the ticket system to remain focused on ticket management while ensuring seamless integration with other authentication systems.

- ### Key Benefits:

1. **Delegated Authentication**:
   - Authentication is handled by external trusted backends, which can generate and manage JWT tokens.
   - The ticket system validates the token without managing user credentials or authentication logic.

2. **Flexibility**:
   - Trusted backends can implement custom user management workflows.
   - Examples:
     - Allowing guest users to create tickets without a full account (`TEMP_USER`).
     - Managing advanced permissions for agents or admins.

3. **Scalability**:
   - By decoupling authentication from the ticket system, both systems can scale independently.

4. **Lightweight Validation**:
   - The ticket system only needs to validate the token using the shared secret key and extract user information, keeping it lightweight and efficient.

5. **Security**:
   - Authentication logic and sensitive data, such as passwords, are handled by external servers, reducing security risks on the ticket system.


- **Payload of Token:** 
```{
    "id": "string",
    "username": "string",
    "email": "valid_email_string"
    "role": "string"
}
```
- **Role:** ``TEMP_USER, CUSTOMER, AGENT, ADMIN``


# Objects

### Ticket Object
```json
{
  "id": "string",
  "user_id": "string",
  "topic": "string",
  "description": "string",
  "status": "string",
  "created_at": "integer",
  "updated_at": "integer",
  "user_role": "string",
  "support_role": "string",
  "issue_level": "string"
}
```
- **User Role:** TEMP_USER, CUSTOMER, AGENT, ADMIN
- **Support Team Role:** GENERAL, TECHNICAL, MANAGER, ADMIN
- **Issue Level:** NORMAL, URGENT, CRITICAL

### Message Object
```json
{
  "id": "string",
  "ticket_id": "string",
  "author_id": "string",
  "author_name": "string",
  "content": "string",
  "attachments": ["http://example.com/attachment1.png","http://example.com/attachment2.png"],
  "created_at": "integer",
  "updated_at": "integer"
}
```


# Endpoints

## Tickets

#### Create Ticket

- **URL:** `/api/v1/tickets`
- **Method:** `POST`
- **Rate Limit:** `3 per minute`
- **Response:** ``Ticket Object``
- **Authentication:** Required
- **Description:** Creates a new ticket.
- **Request Body:**
```json
  {
    "topic": "string",
    "description": "string"
  }
```

#### Get All Tickets
- **URL:** `/api/v1/tickets`
- **Method:** `GET`
- **Rate Limit:** `30 per minute`
- **Response:** ``Array[Ticket Object]``
- **Authentication:** Required
- **Description:** Creates a new ticket.




#### Get Ticket
- **URL:** `/api/v1/tickets/<ticket_id>`
- **Method:** `GET`
- **Rate Limit:** `30 per minute`
- **Response:** ``Ticket Object``
- **Authentication:** Required
- **Description:** Creates a new ticket.

## Messages

#### Send Message
- **URL:** `/api/v1/tickets/<ticket_id>/messages`
- **Method:** `POST`
- **Rate Limit:** `15 per minute`
- **Response:** ``Message Object``
- **Authentication:** Required
- **Description:** Send the message to the ticket
- **Request Body:**
```json
  {
    "content": "string",
  }
```

#### Get Messages
- **URL:** `/api/v1/tickets/<ticket_id>/messages`
- **Method:** `GET`
- **Rate Limit:** `15 per minute`
- **Response:** ``Message Object``
- **Authentication:** Required
- **Description:** All Messages of the ticket


# Socket Connection

## Server Events

### Authentication
- **Event Name:** ``authorize``
- **Description:** After the socket connection user is required to authorize them after that they will receive all the events 
- **Request Body:**
```json
{
    "token": "string"
}
```

## Client Events

### Error
### New Message
- **Event Name:** ``error``
- **Data:** 
```json
{
    "message": "Error Message"
}
```
- **Description:** Event is sent when a new message is sent to the user


### New Message
- **Event Name:** ``message``
- **Data:** ``Message Object``
- **Description:** Event is sent when a new message is sent to the user

### Edit Message
- **Event Name:** ``edit_message``
- **Data:** ``Message Object``
- **Description:** Event is sent when the message is edited from other party


### Edit Message
- **Event Name:** ``delete_message``
- **Data:** ``Message Object``
- **Description:** Event is sent when the message is deleted by other party

### Ticket Close
- **Event Name:** ``ticket_closed``
- **Data:** ``Ticket Object``
- **Description:** Event is sent when the message is deleted by other party



# Errors

### Bad Request
- **Status Code:** 400
- **Response:**
```json
 {
    "error": "BAD_REQUEST",
    "message": "Invalid form of body",
    "errors": [
      {
        "location": "field_name",
        "message": "Description of the validation error",
        "type": "error_type",
        "context": "additional_context_if_any"
      }
    ]
  }
```

### Authentication
- **Status Code:** 401
- **Response:**
 ```json
{
    "error": "UNAUTHORIZED",
    "message": "Error message"
}
```

### Accesss Denied
- **Status Code:** 403
- **Response:**
 ```json
{
    "error": "FORBIDDEN",
    "message": "Error message"
}
```

### Not Found
- **Status Code:** 404
- **Response:**
 ```json
{
    "error": "NOT_FOUND",
    "message": "Error message"
}
```

### Ratelimit
- **Status Code:** 429
- **Response:**
```json
{
    "error": "RATELIMIT",
    "message": "You are being ratelimited only X request are allowed"
}
```

### Internal Server Error
- **Status Code:** 500
- **Response:**
```json
{
    "error": "INTERNAL_SERVER_ERROR", 
    "message": "Error message"
}
```


# Enviroment Variables
- All the fields mentioned as ``<field>`` will be replaced with actual values
```
# Web Server Port
WEB_SERVER_PORT=5000

# PRODUCTION or DEVELOPMENT
SERVER_MODE=DEVELOPMENT 


# MongoDB URI
MONGO_URI=<uri_of_db>

# Name of database
DB_NAME=<support_ticket_db>


# Discord Settings
DISCORD_BOT_TOKEN=<token_of_bot>
GUILD_ID=<id_of_guild>



# Discord Transcript Channel ID
TRANSCRIPT_CHANNEL_ID=<id_of_channel>


# Category IDs
GENERAL_TICKET_CATEGORY_ID=<id_of_category>
CRITICAL_TICKET_CATEGORY_ID=<id_of_category>
URGENT_TICKET_CATEGORY_ID=<id_of_category>


# Role IDs
ADMIN_ROLE_ID=<id_of_role>
MANAGER_ROLE_ID=<id_of_role>
DEVELOPER_ROLE_ID=<id_of_role>
SUPPORT_TEAM_ROLE_ID=<id_of_role>


# Secret Keys
JWT_SECRET_KEY=<super_secret_key>


# # Discord Webhook URL for Logs
ERROR_WEBHOOK_URL=<discord_channel_webhook_url>
ERROR_BOT_WEBHOOK_URL=<discord_channel_webhook_url>
```


# Example Code for Socket Connection
```js
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:5000';
const token = '<your_jwt_token>';

const socket = io(SOCKET_URL, {
  query: { token },
});

// Listen for events
socket.on('message', (data) => {
  console.log('New message:', data);
  // Handle the data
});

socket.on('edit_message', (data) => {
  console.log('Message edited:', data);
    // Handle the data

});

socket.on('delete_message', (data) => {
  console.log('Message Deleted:', data);
    // Handle the data

});

socket.on('ticket_closed', (data) => {
  console.log('Ticket closed:', data);
    // Handle the data

});

// Authorize after connecting
socket.emit('authorize', { token });
```










