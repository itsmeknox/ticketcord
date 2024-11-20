from discord.ext import commands

from utils.schema import Ticket, Message

from database.tickets import fetch_ticket
from database.messages import insert_message

from socket_manager.send_events import send_message_event

import asyncio
import discord

from utils.enums import TicketStatus

from utils.settings import guild_settings


class MessageHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, discord_message: discord.Message):
        if discord_message.author.bot:
            return
        


        elif discord_message.mentions:
            print("Mention found returning")
            return
        
        ticket: Ticket = await asyncio.to_thread(fetch_ticket, str(discord_message.channel.id))
        if not ticket:
            print("Ticket not found returning")
            return
        
        if ticket.status != TicketStatus.ACTIVE:
            print("Ticket is not active returning")
            return
        
        if not discord_message.content:
            print("Message has no content returning")
            return
        
        

        message = Message(
            ticket_id=ticket.id,
            author_id=str(discord_message.author.id),
            author_name=discord_message.author.display_name or discord_message.author.name,
            content=discord_message.content,
            attachments=[attachment.url for attachment in discord_message.attachments]
        )
        insert_message(message)
        send_message_event(user_id=ticket.user_id, message=message)
        
        print("Message sent: ", message.content)
        if guild_settings.replay_to_success_message:
            await discord_message.reply("Message sent successfully!..", delete_after=5)
        
        
