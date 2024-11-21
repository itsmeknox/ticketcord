from discord.ext import commands

from utils.schema import Ticket, Message

from database.tickets import fetch_ticket
from database.messages import insert_message, update_message_content, delete_message

from socket_manager.send_events import send_message_event, message_edit_event, message_delete_event

import asyncio
import discord

from utils.enums import TicketStatus

from utils.settings import guild_settings

import logging

logger = logging.getLogger("bot_logger")

def filter_message(message: discord.Message):
    return not message.author.bot and not message.mentions

async def fetch_active_ticket(channel_id: str) -> Ticket:
    ticket: Ticket = await asyncio.to_thread(fetch_ticket, channel_id)
    if not ticket:
        print(f"Ticket not found for channel ID: {channel_id}")
        return None
    
    if ticket.status != TicketStatus.ACTIVE:
        print(f"Ticket {ticket.id} is not active")
        return None
    return ticket

class MessageHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, discord_message: discord.Message):
        if not filter_message(discord_message):
            print("Message filtered out")
            return

        ticket = await fetch_active_ticket(str(discord_message.channel.id))
        if not ticket:
            return

        if not discord_message.content:
            print("Message has no content")
            return

        message = Message(
            id=str(discord_message.id),
            ticket_id=ticket.id,
            author_id=str(discord_message.author.id),
            author_name=discord_message.author.display_name or discord_message.author.name,
            content=discord_message.content,
            attachments=[attachment.url for attachment in discord_message.attachments]
        )
        insert_message(message)
        send_message_event(user_id=ticket.user_id, message=message)

        print(f"Message sent: {message.content}")
        if guild_settings.replay_to_success_message:
            await discord_message.reply("Message sent successfully!..", delete_after=5)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        ticket = await fetch_active_ticket(str(before.channel.id))
        if not ticket:
            return

        if not after.content:
            print("Edited message has no content")
            return

        message = await asyncio.to_thread(update_message_content, str(before.channel.id), str(before.id), after.content)
        if not message:
            print("Message not found, failed to edit")
            return

        message_edit_event(user_id=ticket.user_id, message=message)

        print(f"Message edited: {message.content}")
        await after.reply("Message edited successfully!..", delete_after=5)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        ticket = await fetch_active_ticket(str(message.channel.id))
        if not ticket:
            return

        message = await asyncio.to_thread(delete_message, str(message.id))
        if not message:
            print("Message not found, failed to delete")
            return

        print(f"Message deleted: {message.content}")
        message_delete_event(user_id=ticket.user_id, message=message)

