from discord.ext import commands

from utils.schema import Ticket, Message

from database.tickets import fetch_ticket
from database.messages import insert_message

from socket_manager.send_events import send_message_event

import asyncio
import discord




class MessageHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        elif message.mentions:
            print("Mention found returning")
            return
        
        ticket: Ticket = await asyncio.to_thread(fetch_ticket, message.channel.id)
        if not ticket:
            print("Ticket not found returning")
            return
        
        message = Message(
            ticket_id=ticket.id,
            author_id=message.author.id,
            author_name=message.author.display_name or message.author.name,
            content=message.content,
            attachments=[attachment.url for attachment in message.attachments]
        )
        insert_message(message)
        send_message_event(user_id=ticket.user_id, message=message)
        
        print("Message sent: ", message.content)
        
        
        
        
