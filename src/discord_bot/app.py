from discord.ext import commands
import discord
import os
import threading
import asyncio
import threading

from .ticket_handler import TicketManager, TranscriptView
from .message_handler import MessageHandler
from chat_exporter import export

from database.tickets import update_ticket_status, update_ticket
from socket_manager.send_events import ticket_close_event
from utils.enums import TicketStatus, SupportRole, IssueLevel
from utils.settings import guild_settings

from discord import option

bot = commands.Bot(intents=discord.Intents.all())
ticket_manager = TicketManager(bot=bot)

is_running = threading.Event()

bot_lock = threading.Lock()

def bot_run_async_coroutine(coro):
    """
    Runs a coroutine object on the bot's event loop.
    
    Args:
        coro (coroutine): The coroutine object to execute.
        
    Returns:
        Any: The result of the coroutine, or raises an exception if it fails.
    """
    with bot_lock:
        future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            return future.result(timeout=10)  # Adjust timeout as needed
        except Exception as e:
            raise e


    


@bot.event
async def on_ready():
    global is_running
    print(f"Succesfully logged in as {bot.user}")
    ticket_manager.initialize()
    is_running.set()
    
    bot.add_view(TranscriptView())


@bot.slash_command(name="delete_ticket")
async def delete_ticket(ctx: discord.ApplicationContext, reason: str):
    # Remove the first query to fetch the ticket
    # ticket = fetch_ticket(ctx.interaction.channel.id)
    # if not ticket:
    #     await ctx.respond(f"This channel is not a ticket channel.", ephemeral=True)
    
    # Update the ticket status and get the updated ticket
    ticket = update_ticket_status(ctx.interaction.channel_id, TicketStatus.CLOSED)
    if not ticket:
        await ctx.respond(f"Failed to update ticket status in database", ephemeral=True)
        return

    ticket_close_event(ticket.user_id, ticket.id)
        
    await ctx.respond(embed=discord.Embed(title="Ticket Closed", description="This ticket has been closed deleting..."))
    
    transcript_file = await export(ctx.interaction.channel)
    await ticket_manager.send_transcript(ticket, transcript_file, reason)
    await ctx.interaction.channel.delete()


# Assign Role
@bot.slash_command(name="assign_role", description="Assign a role and move the ticket to a category.")
@option(
    "role",
    description="Select a role to assign",
    choices=[role.value for role in SupportRole],  # Use enum values for consistency
    required=True
)
@option(
    "issue_level",
    description="Select the issue level",
    choices=[level.value for level in IssueLevel],  # Use enum values for consistency
    required=True
)
async def assign_role(
    ctx: discord.ApplicationContext,
    role: str,
    issue_level: str,
    note: str = None
):
    await ctx.defer()

    # Map inputs to enums
    support_role_mapping = {role.value: role for role in SupportRole}
    issue_level_mapping = {level.value: level for level in IssueLevel}

    support_role = support_role_mapping.get(role)
    issue_level_enum = issue_level_mapping.get(issue_level)

    if not support_role:
        return await ctx.respond("Invalid role selected.", ephemeral=True)

    if not issue_level_enum:
        return await ctx.respond("Invalid issue level selected.", ephemeral=True)

    # Update the ticket in the database
    ticket = update_ticket(
        id=str(ctx.interaction.channel_id),
        support_role=support_role,
        issue_level=issue_level_enum.value
    )

    if not ticket:
        return await ctx.respond("This channel is not a ticket channel.", ephemeral=True)


    # Edit channel category based on issue level
    if issue_level_enum == IssueLevel.URGENT:
        await ctx.interaction.channel.edit(category=ticket_manager.urgent_category)
    elif issue_level_enum == IssueLevel.CRITICAL:
        await ctx.interaction.channel.edit(category=ticket_manager.critical_category)
    else:
        await ctx.interaction.channel.edit(category=await ticket_manager.get_ticket_category())

    # Build the embed message
    note_message = f"\nNote: {note}" if note else ""
    embed = discord.Embed(
        title="Role Assigned",
        description=f"Role: {support_role.value}\nIssue Level: {issue_level}{note_message}",
        color=discord.Color.blue()
    )

    role_mention = {
        SupportRole.ADMIN: guild_settings.admin_role_id,
        SupportRole.MANAGER: guild_settings.manager_role_id,
        SupportRole.TECHNICAL: guild_settings.developer_role_id,
        SupportRole.GENERAL: guild_settings.support_team_role_id
    }.get(support_role, guild_settings.support_team_role_id)

    if not role_mention:
        return await ctx.respond("Role mention configuration is missing.", ephemeral=True)

    await ctx.interaction.channel.send(f"<@&{role_mention}>", embed=embed)
    await ctx.respond(f"Ticket successfully updated with role {role} and issue level {issue_level}.")



@bot.slash_command(name="delete_all_channels_in_category")
async def create_ticket(ctx: discord.ApplicationContext):
    await ctx.respond("Deleting the tickets")
    channels = ctx.interaction.channel.category.channels
    
    for channel in channels:
        await channel.delete()
          


bot.add_cog(MessageHandler(bot))

def run_bot():
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN is not set in the environment variables")
    
    def run():
        bot.run(BOT_TOKEN)
    
    threading.Thread(target=run, daemon=True).start()
    is_running.wait()
